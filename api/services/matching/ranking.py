"""语义精排 —— 向量相似度 + 多维加权评分 + 置信度感知排序"""

from typing import List, Dict, Any, Optional, Tuple
import logging

from services.matching.schemas import (
    EnhancedDemandProfile,
    EnhancedOPCProfile,
    EnhancedMatchResult,
    MatchDetail,
)
from services import embedding as embed_utils

logger = logging.getLogger("uvicorn")

# 评分权重（初始经验值，后续 AB 调优）
WEIGHTS = {
    "semantic_similarity": 0.30,
    "skill_match": 0.25,
    "experience_match": 0.15,
    "reputation": 0.12,
    "response_speed": 0.10,
    "budget_match": 0.08,
}


def compute_semantic_similarity(
    demand: EnhancedDemandProfile,
    opc: EnhancedOPCProfile,
) -> float:
    """计算需求与 OPC 能力的语义向量相似度"""
    # 需求侧文本
    demand_parts = []
    if demand.primary_need.value:
        demand_parts.append(demand.primary_need.value)
    if demand.domain.value:
        demand_parts.append(demand.domain.value)
    if demand.description.value:
        demand_parts.append(demand.description.value)
    demand_text = " ".join(demand_parts)

    # 供给侧文本
    opc_parts = [opc.bio]
    for skill_info in opc.capabilities.get("primary_skills", []):
        if isinstance(skill_info, dict):
            opc_parts.append(skill_info.get("skill", ""))
        else:
            opc_parts.append(str(skill_info))
    for domain in opc.capabilities.get("domains", []):
        opc_parts.append(str(domain))
    opc_text = " ".join(opc_parts)

    if not demand_text.strip() or not opc_text.strip():
        return 0.5

    try:
        embeddings = embed_utils.embed_texts([demand_text, opc_text])
        if len(embeddings) == 2:
            return embed_utils.cosine_similarity(embeddings[0], embeddings[1])
    except Exception as e:
        logger.warning(f"[Ranking] 向量相似度计算失败: {e}")

    return 0.5


def compute_skill_match(
    demand: EnhancedDemandProfile,
    opc: EnhancedOPCProfile,
) -> float:
    """计算技能匹配度（考虑 mandatory/optional + 熟练度加权）"""
    required = set(demand.required_skills.value)
    mandatory = set(demand.required_skills.mandatory)
    optional = set(demand.required_skills.optional)

    opc_skills = {}
    for s in opc.capabilities.get("primary_skills", []):
        if isinstance(s, dict):
            opc_skills[s.get("skill", "").lower()] = s.get("level", 0.5)
        else:
            opc_skills[str(s).lower()] = 0.5
    for s in opc.capabilities.get("secondary_skills", []):
        if isinstance(s, dict):
            name = s.get("skill", "").lower()
            if name not in opc_skills:
                opc_skills[name] = s.get("level", 0.3)
        else:
            name = str(s).lower()
            if name not in opc_skills:
                opc_skills[name] = 0.3

    if not required:
        return 0.5

    score = 0.0
    total_weight = 0.0

    for skill in required:
        skill_lower = skill.lower()
        weight = 1.5 if skill in mandatory else 1.0
        total_weight += weight

        # 精确匹配
        if skill_lower in opc_skills:
            score += opc_skills[skill_lower] * weight
            continue

        # 模糊匹配（包含关系）
        matched = False
        for opc_skill, level in opc_skills.items():
            if skill_lower in opc_skill or opc_skill in skill_lower:
                score += level * weight * 0.8
                matched = True
                break
        if not matched:
            # 无匹配
            score += 0.0

    return score / total_weight if total_weight > 0 else 0.0


def compute_experience_match(
    demand: EnhancedDemandProfile,
    opc: EnhancedOPCProfile,
) -> float:
    """计算经验匹配度"""
    score = 0.0

    # 复杂度匹配
    demand_complexity = demand.complexity.value
    opc_scale = opc.capabilities.get("typical_project_scale", "medium")
    if demand_complexity == opc_scale:
        score += 0.6
    elif demand_complexity == "low" and opc_scale in ("medium", "low"):
        score += 0.4
    elif demand_complexity == "medium" and opc_scale in ("medium", "high"):
        score += 0.4

    # 项目类型重叠
    demand_type = demand.primary_need.value or ""
    past_types = opc.capabilities.get("past_project_types", [])
    if demand_type and demand_type in past_types:
        score += 0.4

    return min(1.0, score)


def compute_reputation_score(opc: EnhancedOPCProfile) -> float:
    """计算信誉得分"""
    rating = opc.reputation.get("rating", 3.0) or 3.0
    completion = opc.reputation.get("completion_rate", 1.0) or 1.0
    return (rating / 5.0) * 0.7 + min(1.0, completion) * 0.3


def compute_response_score(opc: EnhancedOPCProfile) -> float:
    """计算响应速度得分"""
    avg_hours = opc.availability.get("avg_response_hours", 24) or 24
    return max(0.0, 1.0 - avg_hours / 24)


def compute_budget_match(
    demand: EnhancedDemandProfile,
    opc: EnhancedOPCProfile,
) -> float:
    """计算预算匹配度"""
    d_budget = demand.estimated_budget_range.value
    d_min = d_budget.get("min")
    d_max = d_budget.get("max")

    o_min = opc.pricing.get("min_rate", 0) or 0
    o_max = opc.pricing.get("max_rate", float("inf")) or float("inf")

    if d_min is None and d_max is None:
        return 0.5  # 需求侧无预算信息，中性分

    # 计算区间重叠比例
    if d_min is not None and d_max is not None:
        overlap = min(d_max, o_max) - max(d_min, o_min)
        if overlap <= 0:
            return 0.0
        demand_range = d_max - d_min
        return min(1.0, overlap / demand_range) if demand_range > 0 else 0.8
    elif d_min is not None:
        return 0.8 if d_min <= o_max else 0.2
    elif d_max is not None:
        return 0.8 if d_max >= o_min else 0.2
    return 0.5


def compute_final_score(
    demand: EnhancedDemandProfile,
    opc: EnhancedOPCProfile,
    sim_embedding: Optional[float] = None,
) -> Tuple[float, MatchDetail]:
    """
    计算最终加权得分。

    返回: (final_score, MatchDetail)
    """
    if sim_embedding is None:
        sim_embedding = compute_semantic_similarity(demand, opc)

    sim_skills = compute_skill_match(demand, opc)
    sim_exp = compute_experience_match(demand, opc)
    score_reputation = compute_reputation_score(opc)
    score_response = compute_response_score(opc)
    score_budget = compute_budget_match(demand, opc)

    final_score = (
        sim_embedding * WEIGHTS["semantic_similarity"]
        + sim_skills * WEIGHTS["skill_match"]
        + sim_exp * WEIGHTS["experience_match"]
        + score_reputation * WEIGHTS["reputation"]
        + score_response * WEIGHTS["response_speed"]
        + score_budget * WEIGHTS["budget_match"]
    )

    detail = MatchDetail(
        semantic_similarity=round(sim_embedding, 4),
        skill_match=round(sim_skills, 4),
        experience_match=round(sim_exp, 4),
        reputation_score=round(score_reputation, 4),
        response_score=round(score_response, 4),
        budget_match=round(score_budget, 4),
        confidence_penalty=0.0,
        final_score=round(final_score, 4),
    )

    return final_score, detail


def confidence_aware_ranking(
    candidates: List[EnhancedOPCProfile],
    demand: EnhancedDemandProfile,
    top_k: int = 8,
) -> List[EnhancedMatchResult]:
    """
    置信度感知排序：
    - 对候选 OPC 做多维评分
    - 低置信维度施加软惩罚
    - 返回 Top-K 结果
    """
    if not candidates:
        return []

    # 预计算需求侧 embedding（只算一次）
    demand_parts = []
    if demand.primary_need.value:
        demand_parts.append(demand.primary_need.value)
    if demand.domain.value:
        demand_parts.append(demand.domain.value)
    if demand.description.value:
        demand_parts.append(demand.description.value)
    demand_text = " ".join(demand_parts)

    scored = []
    for opc in candidates:
        # 计算语义相似度
        opc_parts = [opc.bio]
        for s in opc.capabilities.get("primary_skills", []):
            opc_parts.append(s.get("skill", "") if isinstance(s, dict) else str(s))
        opc_text = " ".join(opc_parts)

        try:
            sim_embedding = 0.5  # default
            if demand_text.strip() and opc_text.strip():
                embeddings = embed_utils.embed_texts([demand_text, opc_text])
                if len(embeddings) == 2:
                    sim_embedding = embed_utils.cosine_similarity(embeddings[0], embeddings[1])
        except Exception:
            sim_embedding = 0.5

        # 多维评分
        final_score, detail = compute_final_score(demand, opc, sim_embedding)

        # 置信度惩罚：低置信维度打折
        penalty = 1.0
        dims = [
            ("primary_need", demand.primary_need),
            ("domain", demand.domain),
            ("required_skills", demand.required_skills),
            ("complexity", demand.complexity),
            ("estimated_budget_range", demand.estimated_budget_range),
            ("timeline", demand.timeline),
        ]
        for _, dim in dims:
            if dim.confidence < 0.5:
                penalty *= 0.85

        detail.confidence_penalty = round(1.0 - penalty, 4)
        final_score *= penalty
        detail.final_score = round(final_score, 4)

        # 构建匹配理由
        reasons = _build_match_reasons(demand, opc, detail)

        scored.append(EnhancedMatchResult(
            opc=opc,
            score=round(final_score, 4),
            detail=detail,
            match_reasons=reasons,
        ))

    scored.sort(key=lambda x: x.score, reverse=True)
    return scored[:top_k]


def _build_match_reasons(
    demand: EnhancedDemandProfile,
    opc: EnhancedOPCProfile,
    detail: MatchDetail,
) -> List[str]:
    """构建匹配理由文本"""
    reasons = []

    if detail.skill_match > 0.6:
        skills = demand.required_skills.value
        if skills:
            matched = [s for s in skills[:3] if _skill_in_opc(s, opc)]
            if matched:
                reasons.append(f"技能匹配度高：{'、'.join(matched)} 等技能对口")
            else:
                reasons.append(f"技能结构匹配你的需求")

    if detail.experience_match > 0.7:
        reasons.append("项目经验与你需求相符")

    if detail.reputation_score > 0.8:
        reasons.append("高信誉评分，交付有保障")

    if detail.response_score > 0.9:
        reasons.append("响应速度快，沟通效率高")

    if not reasons:
        reasons.append("综合能力适合你的项目需求")

    return reasons


def _skill_in_opc(skill: str, opc: EnhancedOPCProfile) -> bool:
    """检查技能是否存在于 OPC 技能列表中"""
    skill_lower = skill.lower()
    for s in opc.capabilities.get("primary_skills", []):
        name = s.get("skill", "").lower() if isinstance(s, dict) else str(s).lower()
        if skill_lower in name or name in skill_lower:
            return True
    return False
