"""用户需求画像管理 —— CRUD + 增量更新"""

from typing import Dict, Any, Optional
from db.supabase import _get, _post, _patch


def get_demand_profile(session_id: str) -> Optional[Dict[str, Any]]:
    """获取已有的需求画像"""
    rows = _get(
        "demand_profiles",
        params={
            "select": "*",
            "session_id": f"eq.{session_id}",
            "is_deleted": "eq.false",
        },
    )
    return rows[0] if rows else None


def save_demand_profile_enhanced(profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    保存增强版需求画像（按 session_id 去重）。
    保存增强字段：inference_meta、behavioral_signals 存为 JSON 字符串。
    """
    import json

    session_id = profile.get("session_id", "")
    existing = _get(
        "demand_profiles",
        params={
            "select": "id",
            "session_id": f"eq.{session_id}",
            "is_deleted": "eq.false",
        },
    )

    # 映射到 DB 列
    db_columns = {
        "session_id", "user_id", "project_type", "budget_min", "budget_max",
        "timeline", "skills_required", "description", "status",
        "project_scope", "industry",
    }

    clean = {}
    for k, v in profile.items():
        if k in db_columns:
            clean[k] = v

    # 增强字段序列化
    if "overall_confidence" in profile:
        clean["project_scope"] = json.dumps({
            "overall_confidence": profile.get("overall_confidence"),
            "inference_cost": profile.get("inference_cost", {}),
        }, ensure_ascii=False)

    if "industry" not in clean and profile.get("industry"):
        clean["industry"] = profile["industry"]

    if existing:
        return _patch("demand_profiles", clean, "id", existing[0]["id"])
    else:
        return _post("demand_profiles", clean)


def update_user_behavior(user_id: str, signal: Dict[str, Any]) -> None:
    """更新用户行为信号（追加式）"""
    existing = get_demand_profile(user_id) or {}
    existing_signals = existing.get("behavioral_signals", {})

    # 合并信号
    for key in ["search_queries", "viewed_opc_ids"]:
        if key in signal:
            existing_list = existing_signals.get(key, [])
            new_items = signal[key]
            if isinstance(new_items, list):
                existing_signals[key] = list(set(existing_list + new_items))

    for key in ["time_spent_categories"]:
        if key in signal:
            existing_dict = existing_signals.get(key, {})
            for cat, seconds in signal[key].items():
                existing_dict[cat] = existing_dict.get(cat, 0) + seconds
            existing_signals[key] = existing_dict

    # TODO: 将更新的 behavioral_signals 写回 DB
