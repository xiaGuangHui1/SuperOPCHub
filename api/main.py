"""Super OPC Hub — AI 匹配后端服务

FastAPI 应用，提供两个核心接口：
  POST /api/chat    — 发送对话消息，获取 AI 回复 + 需求提取 + 匹配结果
  GET  /api/health  — 健康检查

使用方式：
  uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    ChatRequest,
    ChatResponse,
    MatchResponse,
    DemandProfileOut,
    OPCMatch,
)
from services import extraction
from services.matching import match_opc_profiles
from db.supabase import fetch_opc_profiles, save_demand_profile, save_conversation_message
from config import config

app = FastAPI(
    title="Super OPC Hub API",
    description="AI 驱动的需求提取与 OPC 精准匹配服务",
    version="0.1.0",
)

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
def chat(request: ChatRequest):
    """
    核心对话接口。

    接收用户的对话消息，执行以下流程：
    1. 调用 LLM 从对话中提取结构化需求画像
    2. 如果需求不完整，生成追问引导消息
    3. 如果需求完整，执行多维度 OPC 匹配
    4. 保存对话记录到数据库
    5. 返回 AI 回复 + 需求画像 + 匹配结果
    """
    session_id = request.session_id
    messages = request.messages

    # ── Step 1: 提取需求画像 ──────────────────────
    demand_profile = extraction.extract_demand_profile(messages)
    demand_profile.session_id = session_id

    # ── Step 2: 生成 AI 回复 ──────────────────────
    assistant_message = extraction.generate_assistant_message(messages, demand_profile)

    # ── Step 3: 匹配（仅当需求完整）─────────────────
    matches: list[OPCMatch] = []
    is_matching_complete = False
    if demand_profile.is_complete:
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
                "user_id": request.user_id,
                "project_type": demand_profile.project_type,
                "budget_min": demand_profile.budget_min,
                "budget_max": demand_profile.budget_max,
                "timeline": demand_profile.timeline,
                "skills_required": ",".join(demand_profile.skills_required),
                "description": demand_profile.description,
                "status": "active",
            })
        except Exception:
            pass  # 数据库写入失败不影响主流程

    # ── Step 4: 保存对话记录 ──────────────────────
    try:
        # 保存最新的用户消息
        if messages and messages[-1].role == "user":
            save_conversation_message({
                "user_id": request.user_id,
                "session_id": session_id,
                "role": "user",
                "content": messages[-1].content,
            })
        # 保存 AI 回复
        save_conversation_message({
            "user_id": request.user_id,
            "session_id": session_id,
            "role": "assistant",
            "content": assistant_message,
        })
    except Exception:
        pass

    response = ChatResponse(
        session_id=session_id,
        assistant_message=assistant_message,
        demand_profile=demand_profile if not is_matching_complete else None,
        matches=matches,
        is_matching_complete=is_matching_complete,
    )

    # 匹配完成时也返回画像
    if is_matching_complete:
        response.demand_profile = demand_profile

    return response


@app.post("/api/match", response_model=MatchResponse)
def match(request: ChatRequest):
    """独立的匹配接口：基于已提取的需求进行匹配（用于手动触发）"""
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
