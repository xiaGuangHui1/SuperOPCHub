"""匹配系统 —— 统一的对外接口

使用方式：
    from services.matching import match_opc_profiles, run_matching_pipeline

    # 旧版关键词匹配
    matches = match_opc_profiles(demand, opc_profiles)

    # 新版 Agent 流水线
    result = run_matching_pipeline(
        user_input="用户触发匹配的文本",
        session_id="会话ID",
        user_id="用户ID",
        initial_extraction={"project_type": "...", ...},
    )
"""

from typing import List, Dict, Any, Optional
import logging
import re

from models.schemas import DemandProfileOut, OPCMatch

logger = logging.getLogger("uvicorn")


# ═══════════════════════════════════════════════════════
# 旧版关键词匹配（V0 —— 保持兼容）
# ═══════════════════════════════════════════════════════

def match_opc_profiles(
    demand: DemandProfileOut,
    opc_profiles: List[Dict[str, Any]],
    top_k: int = 8,
    min_score: float = 0.0,
) -> List[OPCMatch]:
    """简化的关键词匹配（V0 兼容）"""
    if not opc_profiles:
        return []

    search_parts = []
    if demand.project_type:
        search_parts.append(demand.project_type)
    if demand.description:
        search_parts.append(demand.description)
    if demand.industry:
        search_parts.append(demand.industry)
    if demand.skills_required:
        search_parts.append(" ".join(demand.skills_required))
    search_text = " ".join(search_parts)

    if not search_text.strip():
        results = [(p, 50.0) for p in opc_profiles]
    else:
        results = []
        for p in opc_profiles:
            opc_text = " ".join([
                p.get("role") or "",
                p.get("description") or "",
                p.get("skills") or "",
            ])
            score = _keyword_match_score(search_text, opc_text)
            if p.get("is_available", True):
                score = min(100.0, score + 5.0)
            results.append((p, round(score, 1)))

    results.sort(key=lambda x: x[1], reverse=True)
    filtered = [(p, s) for p, s in results if s >= min_score][:top_k]

    matches: List[OPCMatch] = []
    for profile, score in filtered:
        skills = _parse_skills(profile.get("skills") or "")
        role = profile.get("role") or ""
        name = profile.get("name") or ""
        reasons = []
        if score >= 60:
            reasons.append(f"擅长{role}，和你的需求匹配度较高")
        else:
            reasons.append(f"具备{role}能力，可以满足基本需求")

        matches.append(OPCMatch(
            id=profile.get("id", ""),
            name=name,
            avatar_url=profile.get("avatar_url"),
            role=role,
            description=profile.get("description"),
            skills=skills,
            match_rate=score,
            match_reasons=reasons,
            is_available=profile.get("is_available", True),
        ))
    return matches


def _keyword_match_score(search_text: str, opc_text: str) -> float:
    """改进的中文关键词匹配"""
    search_words = re.split(r'[,，、\s]+', search_text)
    search_words = [w.strip() for w in search_words if len(w.strip()) >= 1]
    if not search_words:
        return 30.0

    search_no_space = search_text.replace(" ", "")
    opc_no_space = opc_text.replace(" ", "")
    total = len(search_words)
    hits = 0.0
    for word in search_words:
        if word in opc_text:
            hits += 1.0
            continue
        word_no_space = word.replace(" ", "")
        if len(word_no_space) >= 2 and word_no_space in opc_no_space:
            hits += 0.8
            continue
        if len(word_no_space) >= 2:
            matched = False
            if len(word_no_space) >= 3:
                for i in range(len(word_no_space) - 2):
                    chunk = word_no_space[i:i + 3]
                    if chunk in opc_no_space:
                        hits += 0.6
                        matched = True
                        break
            if not matched:
                for i in range(len(word_no_space) - 1):
                    chunk = word_no_space[i:i + 2]
                    if chunk in opc_no_space:
                        hits += 0.4
                        break

    score = (hits / total) * 100.0
    return max(15.0, min(100.0, score))


def _parse_skills(skills_str: str) -> List[str]:
    """解析逗号分隔的技能字符串"""
    if not skills_str:
        return []
    return [s.strip() for s in skills_str.split(",") if s.strip()]


# ═══════════════════════════════════════════════════════
# V2 增强匹配流水线
# ═══════════════════════════════════════════════════════

from services.matching.agent.orchestrator import RequirementAnalysisAgent
from services.matching.schemas import EnhancedDemandProfile, EnhancedOPCProfile, EnhancedMatchResult
from services.matching.recall import hard_filter
from services.matching.ranking import confidence_aware_ranking
from services.matching.profiles.opc_profile import get_all_opc_profiles
from services.matching.profiles.demand_profile import save_demand_profile_enhanced
from services.matching.feedback import record_feedback


def run_matching_pipeline(
    user_input: str,
    session_id: str,
    user_id: str,
    initial_extraction: Optional[Dict[str, Any]] = None,
    behavioral_signals: Optional[Dict[str, Any]] = None,
    top_k: int = 8,
) -> Dict[str, Any]:
    """
    执行完整的匹配流水线：

    Level 1: 需求推理 Agent（多轮循环）
    Level 2: 候选召回（硬约束过滤）
    Level 3: 语义精排（多因子评分）
    """
    result = {
        "session_id": session_id,
        "demand_profile": None,
        "matches": [],
        "message": "",
    }

    try:
        # ── Level 1: 需求推理 ──────────────────────────
        logger.info(f"[Pipeline] 开始需求推理: session={session_id}")
        agent = RequirementAnalysisAgent(max_rounds=3, confidence_threshold=0.7)
        demand_profile = agent.analyze(
            user_input=user_input,
            behavioral_signals=behavioral_signals,
            initial_extraction=initial_extraction,
        )
        result["demand_profile"] = demand_profile
        result["message"] = _build_ux_message(demand_profile)

        logger.info(
            f"[Pipeline] 推理完成: primary_need={demand_profile.primary_need.value} "
            f"(conf={demand_profile.primary_need.confidence}), "
            f"overall={demand_profile.overall_confidence:.2f}"
        )

        # ── Level 2: 候选召回 ──────────────────────────
        logger.info("[Pipeline] 开始候选召回")
        all_opcs = get_all_opc_profiles()
        if not all_opcs:
            logger.warning("[Pipeline] 无可用 OPC")
            result["message"] += "\n(暂无可用 OPC)"
            return result

        candidates = hard_filter(demand_profile, all_opcs)
        if not candidates:
            logger.info("[Pipeline] 无候选，放宽条件")
            candidates = all_opcs[:20]

        # ── Level 3: 语义精排 ──────────────────────────
        logger.info(f"[Pipeline] 开始语义精排: {len(candidates)} 候选")
        ranked = confidence_aware_ranking(candidates, demand_profile, top_k=top_k)

        result["matches"] = [
            _match_result_to_dict(m) for m in ranked if m.score > 0.3
        ]

        logger.info(
            f"[Pipeline] 匹配完成: {len(result['matches'])} 个结果, "
            f"top_score={ranked[0].score:.3f}" if ranked else "无结果"
        )

        # ── 保存画像 ──────────────────────────────────
        try:
            save_demand_profile_enhanced({
                "session_id": session_id,
                "user_id": user_id,
                "project_type": demand_profile.primary_need.value,
                "description": demand_profile.description.value,
                "industry": demand_profile.industry.value or demand_profile.domain.value,
                "skills_required": ",".join(demand_profile.required_skills.value),
                "timeline": demand_profile.timeline.value,
                "budget_min": demand_profile.estimated_budget_range.value.get("min"),
                "budget_max": demand_profile.estimated_budget_range.value.get("max"),
                "overall_confidence": demand_profile.overall_confidence,
                "status": "active",
            })
        except Exception as e:
            logger.warning(f"[Pipeline] 保存画像失败: {e}")

    except Exception as e:
        logger.error(f"[Pipeline] 匹配流水线异常: {e}", exc_info=True)
        result["message"] = f"匹配过程遇到问题，请稍后重试"

    return result


def _build_ux_message(profile: EnhancedDemandProfile) -> str:
    """构建一次性确认的 UX 文本"""
    parts = ["系统理解你的需求可能是：\n\n"]

    dims = [
        ("项目类型", profile.primary_need),
        ("所属领域", profile.domain),
        ("预估预算", profile.estimated_budget_range, lambda v: f"{v.get('min', '?')}-{v.get('max', '?')}万" if v.get("min") or v.get("max") else "待定"),
        ("期望工期", profile.timeline),
        ("需要技能", profile.required_skills, lambda v: "、".join(v) if v else "待定"),
    ]

    for label, dim, *fmt_func in dims:
        val = dim.value
        conf = dim.confidence

        if isinstance(dim, type(profile.estimated_budget_range)):
            val = dim.value
        elif isinstance(dim, type(profile.required_skills)):
            val = dim.value

        if not val or (isinstance(val, (list, str)) and len(val) == 0):
            continue

        if fmt_func:
            display = fmt_func[0](val)
        else:
            display = str(val) if not isinstance(val, list) else "、".join(val)

        if conf > 0.85:
            mark = "✓"
        elif conf > 0.6:
            mark = "?"
        else:
            mark = "…"

        parts.append(f"{label}：{display}  {mark} (conf={conf:.0%})")

    parts.append("\n以上是否正确？确认后将为你匹配最合适的 OPC。")
    return "\n".join(parts)


def _match_result_to_dict(match: EnhancedMatchResult) -> Dict[str, Any]:
    """将匹配结果转为字典（用于 API 响应）"""
    opc = match.opc
    skills = [
        s.get("skill", "") if isinstance(s, dict) else str(s)
        for s in opc.capabilities.get("primary_skills", [])
    ]

    return {
        "opc_id": opc.opc_id,
        "name": opc.name,
        "bio": opc.bio,
        "role": ", ".join(opc.capabilities.get("domains", [])),
        "description": opc.bio,
        "skills": skills,
        "match_score": round(match.score * 100, 1),
        "match_reasons": match.match_reasons,
        "detail": match.detail.model_dump(),
        "is_available": opc.availability.get("status") == "available",
        "avatar_url": None,
    }
