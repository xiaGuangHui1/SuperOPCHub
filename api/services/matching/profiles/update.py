"""画像增量更新 —— 在用户交互后更新需求画像"""

from typing import Dict, Any, Optional
from services.matching.schemas import EnhancedDemandProfile


def update_demand_after_confirmation(
    profile: EnhancedDemandProfile,
    corrections: Dict[str, Any],
) -> EnhancedDemandProfile:
    """
    用户确认/修正后更新画像。

    :param corrections: {field_name: corrected_value} 被用户修改的字段
    """
    # 记录修正
    for field, new_val in corrections.items():
        profile.user_corrections[field] = {
            "original": str(getattr(profile, field, {}).value if hasattr(getattr(profile, field, None), "value") else ""),
            "corrected_to": str(new_val),
        }

        # 更新对应的维度值
        if hasattr(profile, field):
            dim = getattr(profile, field)
            if hasattr(dim, "value"):
                dim.value = new_val
                dim.confidence = 1.0  # 用户确认的字段置信度为 1
                dim.verified = True
                dim.sources.append("user_correction")

    return profile


def update_demand_with_behavior(
    profile: EnhancedDemandProfile,
    signal: Dict[str, Any],
) -> EnhancedDemandProfile:
    """将行为信号融入画像"""
    signals = profile.behavioral_signals

    if "viewed_opc_ids" in signal:
        existing = signals.get("viewed_opc_ids", [])
        new_ids = signal["viewed_opc_ids"]
        signals["viewed_opc_ids"] = list(set(existing + new_ids))

    if "search_queries" in signal:
        existing = signals.get("search_queries", [])
        new = signal["search_queries"]
        signals["search_queries"] = list(set(existing + new))

    if "time_spent_categories" in signal:
        existing = signals.get("time_spent_categories", {})
        for cat, secs in signal["time_spent_categories"].items():
            existing[cat] = existing.get(cat, 0) + secs
        signals["time_spent_categories"] = existing

    profile.behavioral_signals = signals
    return profile
