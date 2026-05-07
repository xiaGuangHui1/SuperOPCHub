"""候选召回 —— 置信度门控的硬约束过滤"""

from typing import List, Dict, Any, Optional
import logging

from services.matching.schemas import EnhancedDemandProfile, EnhancedOPCProfile

logger = logging.getLogger("uvicorn")


def hard_filter(
    demand: EnhancedDemandProfile,
    opc_profiles: List[EnhancedOPCProfile],
) -> List[EnhancedOPCProfile]:
    """
    硬约束过滤：只对高置信度维度做硬约束。

    规则：
    1. 领域匹配（confidence > 0.5）
    2. 必需技能最小命中（confidence > 0.5, mandatory 技能命中 ≥ N-1）
    3. 可用性过滤
    4. 信誉门槛
    """
    candidates = list(opc_profiles)
    initial_count = len(candidates)

    # 1. 领域匹配
    if demand.domain.confidence > 0.5 and demand.domain.value:
        domain_val = demand.domain.value
        candidates = [
            o for o in candidates
            if domain_val in o.capabilities.get("domains", [])
            or domain_val in (o.capabilities.get("service_types", []))
        ]
        logger.info(f"[Recall] 领域过滤({domain_val}): {initial_count} → {len(candidates)}")

    # 2. 技能最小命中
    if demand.required_skills.confidence > 0.5:
        mandatory = demand.required_skills.mandatory
        if mandatory:
            required_hits = max(1, len(mandatory) - 1)
            before = len(candidates)
            candidates = [
                o for o in candidates
                if _count_skill_hits(mandatory, o) >= required_hits
            ]
            logger.info(f"[Recall] 技能过滤(mandatory={mandatory}): {before} → {len(candidates)}")

    # 3. 可用性
    candidates = [
        o for o in candidates
        if o.availability.get("status") != "unavailable"
    ]

    # 4. 信誉门槛
    candidates = [
        o for o in candidates
        if o.reputation.get("rating", 0) >= 3.0
    ]

    logger.info(f"[Recall] 最终候选: {initial_count} → {len(candidates)}")

    # 兜底：至少返回 5 个结果
    if len(candidates) < 5:
        logger.info(f"[Recall] 候选不足，放宽条件")
        return opc_profiles[:20]

    return candidates


def _count_skill_hits(
    required: List[str],
    opc: EnhancedOPCProfile,
) -> int:
    """计算必需技能在 OPC 技能列表中的命中数"""
    opc_skills = [
        s.get("skill", "").lower() if isinstance(s, dict) else s.lower()
        for s in opc.capabilities.get("primary_skills", [])
    ]
    opc_skills_str = " ".join(opc_skills)

    hits = 0
    for skill in required:
        skill_lower = skill.lower()
        # 精确匹配或包含匹配
        if skill_lower in opc_skills or skill_lower in opc_skills_str:
            hits += 1
    return hits


def _budget_overlap(
    demand_budget: Dict[str, Optional[float]],
    opc_pricing: Dict[str, Any],
) -> bool:
    """检查预算是否有重叠"""
    d_min = demand_budget.get("min")
    d_max = demand_budget.get("max")

    o_min = opc_pricing.get("min_rate", 0) or 0
    o_max = opc_pricing.get("max_rate", float("inf")) or float("inf")

    # 任一端的预算为 None，视为不限制
    if d_min is None and d_max is None:
        return True
    if d_min is not None and d_max is not None:
        return d_max >= o_min and d_min <= o_max
    if d_min is not None:
        return d_min <= o_max
    if d_max is not None:
        return d_max >= o_min
    return True
