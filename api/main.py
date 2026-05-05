"""Super OPC Hub — AI 匹配后端服务

FastAPI 应用，提供两个核心接口：
  POST /api/chat    — 发送对话消息，获取 AI 回复 + 需求提取 + 匹配结果
  GET  /api/health  — 健康检查

使用方式：
  uvicorn main:app --reload --port 8000

对话流程（渐进式需求澄清，不设轮次上限）：
  1. 提取需求画像 → 2. 生成 AI 引导回复 → 3. 需求完整时触发匹配
  4. 用户可继续对话调整需求，自动重新匹配
"""

import traceback
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    ChatRequest,
    ChatResponse,
    MatchResponse,
    OPCMatch,
    DemandProfileOut,
)
from services import extraction
from services.matching import match_opc_profiles
from db.supabase import fetch_opc_profiles, save_demand_profile, save_conversation_message
from db.auth import get_current_user, get_optional_user
from config import config

logger = logging.getLogger("uvicorn")

app = FastAPI(
    title="Super OPC Hub API",
    description="AI 驱动的需求提取与 OPC 精准匹配服务",
    version="0.2.0",
)


def _user_confirmed_demand(messages: list) -> bool:
    """检测用户最后一条消息是否确认需求"""
    from models.schemas import ChatMessage
    if not messages:
        return False
    last = messages[-1]
    if last.role != "user":
        return False
    text = last.content.strip().lower()
    confirm_words = ["确认", "没问题", "可以", "行", "好", "ok", "是的", "对的", "开始", "匹配"]
    return any(w in text for w in confirm_words) and len(text) < 50

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "model": config.LLM_MODEL}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user_id: str = Depends(get_current_user)):
    """
    核心对话接口。（需认证）

    渐进式需求澄清流程（不设轮次上限）：
    1. 调用 LLM 从对话中提取结构化需求画像
    2. 如果需求不完整，生成引导追问消息
    3. 如果需求完整，执行多维度 OPC 匹配
    4. 用户可继续对话调整需求，自动重新匹配
    5. 保存对话记录到数据库
    6. 返回 AI 回复 + 需求画像 + 匹配结果
    """
    session_id = request.session_id
    messages = request.messages

    try:
        # 统计用户发言轮次（提供给 LLM 作为上下文，不再作为强制收束条件）
        user_round = sum(1 for m in messages if m.role == "user")

        # ── Step 1: 提取需求画像 ──────────────────────
        demand_profile = extraction.extract_demand_profile(messages, user_round)
        demand_profile.session_id = session_id

        # ── Step 2: 生成 AI 回复 ──────────────────────
        assistant_message = extraction.generate_assistant_message(
            messages, demand_profile, user_round
        )

        # ── Step 3: 匹配（第 3 轮自动触发，或需求完整且用户确认）──
        matches: list[OPCMatch] = []
        is_matching_complete = False
        if user_round >= 3 or (demand_profile.is_complete and _user_confirmed_demand(messages)):
            try:
                opc_profiles = fetch_opc_profiles()
                matches = match_opc_profiles(
                    demand_profile,
                    opc_profiles,
                    top_k=config.MATCH_TOP_K,
                    min_score=config.MATCH_MIN_SCORE,
                )
                is_matching_complete = True

                # 保存需求画像
                try:
                    save_demand_profile({
                        "session_id": session_id,
                        "user_id": user_id,
                        "project_type": demand_profile.project_type,
                        "project_scope": demand_profile.project_scope,
                        "budget_min": demand_profile.budget_min,
                        "budget_max": demand_profile.budget_max,
                        "timeline": demand_profile.timeline,
                        "skills_required": ",".join(demand_profile.skills_required),
                        "target_users": demand_profile.target_users,
                        "constraints": demand_profile.constraints,
                        "description": demand_profile.description,
                        "collaboration_mode": demand_profile.collaboration_mode,
                        "industry": demand_profile.industry,
                        "service_expectations": demand_profile.service_expectations,
                        "status": "active",
                    })
                except Exception:
                    pass
            except Exception as match_err:
                logger.error(f"[/api/chat] 匹配失败: {match_err}\n{traceback.format_exc()}")
                assistant_message += (
                    "\n\n（匹配引擎暂时繁忙，已记录您的需求，"
                    f"稍后为您推荐匹配人选。{type(match_err).__name__}）"
                )

        # ── Step 4: 保存对话记录 ──────────────────────
        try:
            if messages and messages[-1].role == "user":
                save_conversation_message({
                    "user_id": user_id,
                    "session_id": session_id,
                    "role": "user",
                    "content": messages[-1].content,
                })
            save_conversation_message({
                "user_id": user_id,
                "session_id": session_id,
                "role": "assistant",
                "content": assistant_message,
            })
        except Exception:
            pass

        return ChatResponse(
            session_id=session_id,
            assistant_message=assistant_message,
            demand_profile=demand_profile,
            matches=matches,
            is_matching_complete=is_matching_complete,
        )

    except Exception as e:
        logger.error(f"[/api/chat] 处理失败: {e}\n{traceback.format_exc()}")

        return ChatResponse(
            session_id=session_id,
            assistant_message=(
                "抱歉，处理您的请求时遇到了一些问题"
                f"（{type(e).__name__}），请稍后重试或换个方式描述您的需求。"
            ),
            demand_profile=DemandProfileOut(session_id=session_id),
            matches=[],
            is_matching_complete=False,
        )


@app.post("/api/match", response_model=MatchResponse)
def match(request: ChatRequest, user_id: str = Depends(get_current_user)):
    """独立的匹配接口：基于已提取的需求进行匹配（需认证）"""
    demand_profile = extraction.extract_demand_profile(request.messages)
    demand_profile.session_id = request.session_id

    opc_profiles = fetch_opc_profiles()
    matches = match_opc_profiles(
        demand_profile,
        opc_profiles,
        top_k=config.MATCH_TOP_K,
        min_score=config.MATCH_MIN_SCORE,
    )

    return MatchResponse(
        session_id=request.session_id,
        demand_profile=demand_profile,
        matches=matches,
    )
