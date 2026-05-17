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
    ChatResponseV2,
    MatchResponse,
    OPCMatch,
    DemandProfileOut,
    EnhancedOPCMatch,
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

        # 记录最后一条用户消息，便于排查
        last_user_msg = messages[-1].content if messages and messages[-1].role == "user" else "(空)"
        logger.info(f"[/api/chat] session={session_id} round={user_round} msg={last_user_msg[:80]}")

        # ── Step 1: 提取需求画像 ──────────────────────
        try:
            demand_profile = extraction.extract_demand_profile(messages, user_round)
        except Exception as e:
            raise RuntimeError(f"[Step1-LLM提取] {type(e).__name__}: {e}") from e
        demand_profile.session_id = session_id

        # 用代码兜底计算 is_complete，不依赖 LLM 是否正确设置
        demand_profile.is_complete = bool(demand_profile.project_type)
        logger.info(
            f"[/api/chat] 提取结果: project_type={demand_profile.project_type!r} "
            f"is_complete={demand_profile.is_complete} "
            f"industry={demand_profile.industry!r} "
            f"skills_required={demand_profile.skills_required} "
            f"llm_is_complete={bool(demand_profile.project_type)}"
        )

        # ── Step 2: 匹配（需求识别出来立刻匹配）─────
        matches: list[OPCMatch] = []
        is_matching_complete = False
        if demand_profile.is_complete:
            try:
                try:
                    opc_profiles = fetch_opc_profiles()
                except Exception as e:
                    raise RuntimeError(f"[Step2-获取OPC] {type(e).__name__}: {e}") from e
                logger.info(f"[/api/chat] 获取到 {len(opc_profiles)} 个 OPC 画像")
                try:
                    matches = match_opc_profiles(
                        demand_profile,
                        opc_profiles,
                        top_k=config.MATCH_TOP_K,
                        min_score=config.MATCH_MIN_SCORE,
                    )
                except Exception as e:
                    raise RuntimeError(f"[Step2-关键词匹配] {type(e).__name__}: {e}") from e
                is_matching_complete = True
                logger.info(
                    f"[/api/chat] 匹配结果: {len(matches)} 个匹配, "
                    f"top_scores={[m.match_rate for m in matches[:3]]}"
                )

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

        # ── Step 3: 生成 AI 回复（传入匹配结果）──────
        try:
            assistant_message = extraction.generate_assistant_message(
                messages, demand_profile, user_round, matches if is_matching_complete else None
            )
        except Exception as e:
            raise RuntimeError(f"[Step3-生成回复] {type(e).__name__}: {e}") from e
        logger.info(
            f"[/api/chat] AI 回复 (前80字): {assistant_message[:80]}..."
            if len(assistant_message) > 80
            else f"[/api/chat] AI 回复: {assistant_message}"
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
        tb = traceback.format_exc()
        logger.error(f"[/api/chat] 处理失败: {e}\n{tb}")

        # 提取可读的错误步骤信息给前端
        err_detail = str(e)
        return ChatResponse(
            session_id=session_id,
            assistant_message=(
                f"抱歉，处理您的请求时遇到了一些问题（{err_detail}），请稍后重试或换个方式描述您的需求。"
            ),
            demand_profile=DemandProfileOut(session_id=session_id),
            matches=[],
            is_matching_complete=False,
        )


@app.get("/api/debug-match")
def debug_match():
    """调试端点：检查 OPC 画像数量和匹配状态（无需认证）"""
    import traceback
    result = {"status": "ok", "opc_count": 0, "errors": []}

    try:
        from db.supabase import fetch_opc_profiles
        opc_profiles = fetch_opc_profiles()
        result["opc_count"] = len(opc_profiles)
        if opc_profiles:
            result["sample"] = {
                "name": opc_profiles[0].get("name"),
                "role": opc_profiles[0].get("role"),
                "skills": (opc_profiles[0].get("skills") or "")[:80],
            }
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"fetch_opc_profiles: {e}\n{traceback.format_exc()}")

    try:
        from services.matching import match_opc_profiles as keyword_match_debug
        from models.schemas import DemandProfileOut
        profile = DemandProfileOut(
            session_id="debug",
            project_type="AI客服",
            description="想用AI接住所有客户咨询",
            skills_required=["AI客服系统", "自然语言处理"],
            is_complete=True,
        )
        matches = keyword_match_debug(profile, opc_profiles, top_k=3)
        result["match_count"] = len(matches)
        result["top_match"] = {
            "name": matches[0].name,
            "role": matches[0].role,
            "score": matches[0].match_rate,
        } if matches else None
    except Exception as e:
        result["errors"].append(f"match_opc_profiles: {e}\n{traceback.format_exc()}")

    try:
        from config import config
        key_masked = (config.SUPABASE_SERVICE_KEY[:10] + "..." + config.SUPABASE_SERVICE_KEY[-4:]) if config.SUPABASE_SERVICE_KEY else "(empty)"
        result["config"] = {
            "SUPABASE_URL": config.SUPABASE_URL,
            "SUPABASE_KEY_masked": key_masked,
            "SUPABASE_KEY_len": len(config.SUPABASE_SERVICE_KEY),
            "MATCH_MIN_SCORE": config.MATCH_MIN_SCORE,
            "MATCH_TOP_K": config.MATCH_TOP_K,
        }
    except Exception as e:
        result["errors"].append(f"config: {e}")

    return result


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


@app.post("/api/chat-v2", response_model=ChatResponseV2)
def chat_v2(request: ChatRequest, user_id: str = Depends(get_current_user)):
    """
    V2 对话接口 —— 使用稳定版 LLM 提取 + 关键词匹配。

    返回格式兼容 ChatResponseV2，内部复用 /api/chat 逻辑。
    """
    session_id = request.session_id
    messages = request.messages

    try:
        user_round = sum(1 for m in messages if m.role == "user")
        last_user_msg = messages[-1].content if messages and messages[-1].role == "user" else "(空)"
        logger.info(f"[/api/chat-v2] session={session_id} round={user_round} msg={last_user_msg[:80]}")

        # ── Step 1: 提取需求画像 ──────────────────────
        demand_profile = extraction.extract_demand_profile(messages, user_round)
        demand_profile.session_id = session_id
        demand_profile.is_complete = bool(demand_profile.project_type)

        # ── Step 2: 关键词匹配 ────────────────────────
        opc_matches: list[OPCMatch] = []
        is_matching_complete = False
        if demand_profile.is_complete:
            try:
                opc_profiles = fetch_opc_profiles()
                logger.info(f"[/api/chat-v2] 获取到 {len(opc_profiles)} 个 OPC")
                opc_matches = match_opc_profiles(
                    demand_profile, opc_profiles,
                    top_k=config.MATCH_TOP_K,
                    min_score=config.MATCH_MIN_SCORE,
                )
                is_matching_complete = len(opc_matches) > 0
            except Exception as e:
                logger.error(f"[/api/chat-v2] 匹配失败: {e}")

        # ── Step 3: 生成 AI 回复 ──────────────────────
        assistant_message = extraction.generate_assistant_message(
            messages, demand_profile, user_round,
            matches=opc_matches if is_matching_complete else None,
        )

        # ── Step 4: 保存对话记录 ──────────────────────
        try:
            if messages and messages[-1].role == "user":
                save_conversation_message({
                    "user_id": user_id, "session_id": session_id,
                    "role": "user", "content": messages[-1].content,
                })
            save_conversation_message({
                "user_id": user_id, "session_id": session_id,
                "role": "assistant", "content": assistant_message,
            })
        except Exception:
            pass

        # 转换为 V2 格式
        v2_matches = [
            EnhancedOPCMatch(
                opc_id=m.id, name=m.name, avatar_url=m.avatar_url,
                role=m.role, description=m.description, skills=m.skills,
                match_score=m.match_rate, match_reasons=m.match_reasons,
                is_available=m.is_available,
            )
            for m in opc_matches
        ]

        return ChatResponseV2(
            session_id=session_id,
            assistant_message=assistant_message,
            demand_profile=None,
            matches=v2_matches,
            is_matching_complete=is_matching_complete,
        )

    except Exception as e:
        logger.error(f"[/api/chat-v2] 处理失败: {e}\n{traceback.format_exc()}")
        return ChatResponseV2(
            session_id=session_id,
            assistant_message=f"抱歉，处理请求时遇到问题，请稍后重试。",
            is_matching_complete=False,
        )
