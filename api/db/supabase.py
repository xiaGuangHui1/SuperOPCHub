"""Supabase 客户端封装 —— 使用 httpx 直连 REST API，避免 supabase-py 版本兼容问题"""

from typing import List, Dict, Any, Optional
import httpx
import json

from config import config


def _build_url(path: str) -> str:
    return f"{config.SUPABASE_URL}/rest/v1/{path}"


def _headers() -> Dict[str, str]:
    return {
        "apikey": config.SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {config.SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
    }


def _get(path: str, params: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """GET 请求，返回数据列表"""
    resp = httpx.get(_build_url(path), headers=_headers(), params=params, timeout=15)
    resp.raise_for_status()
    return resp.json() if resp.text else []


def _post(path: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """POST 请求，插入数据并返回结果"""
    headers = _headers()
    headers["Prefer"] = "return=representation"
    resp = httpx.post(_build_url(path), headers=headers, json=data, timeout=15)
    resp.raise_for_status()
    result = resp.json() if resp.text else None
    return result[0] if isinstance(result, list) and result else result


def _patch(path: str, data: Dict[str, Any], eq_col: str, eq_val: str) -> Optional[Dict[str, Any]]:
    """PATCH 请求，更新数据"""
    headers = _headers()
    headers["Prefer"] = "return=representation"
    url = f"{_build_url(path)}?{eq_col}=eq.{eq_val}"
    resp = httpx.patch(url, headers=headers, json=data, timeout=15)
    resp.raise_for_status()
    result = resp.json() if resp.text else None
    return result[0] if isinstance(result, list) and result else result


def fetch_opc_profiles() -> List[Dict[str, Any]]:
    """获取所有可用 OPC 画像"""
    return _get(
        "opc_profiles",
        params={
            "select": "*",
            "is_deleted": "eq.false",
            "is_available": "eq.true",
        },
    )


def fetch_opc_profiles_by_ids(ids: List[str]) -> List[Dict[str, Any]]:
    """根据 ID 列表获取 OPC 画像"""
    if not ids:
        return []
    # 用 in 过滤器
    ids_filter = ",".join(ids)
    return _get(
        "opc_profiles",
        params={
            "select": "*",
            "id": f"in.({ids_filter})",
            "is_deleted": "eq.false",
        },
    )


def save_demand_profile(profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """保存或更新需求画像（按 session_id 去重）"""
    session_id = profile.get("session_id", "")
    existing = _get(
        "demand_profiles",
        params={
            "select": "id",
            "session_id": f"eq.{session_id}",
            "is_deleted": "eq.false",
        },
    )
    # 过滤掉 DB 表中不存在的列
    db_columns = {
        "session_id", "user_id", "project_type", "budget_min", "budget_max",
        "timeline", "skills_required", "description", "status",
    }
    clean = {k: v for k, v in profile.items() if k in db_columns}

    if existing:
        return _patch("demand_profiles", clean, "id", existing[0]["id"])
    else:
        return _post("demand_profiles", clean)


def save_conversation_message(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """保存单条对话消息"""
    return _post("conversation_history", msg)
