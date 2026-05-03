"""Supabase 客户端封装"""

from typing import List, Dict, Any, Optional
from supabase import create_client, Client

from config import config


_supabase: Optional[Client] = None


def get_supabase() -> Client:
    """获取 Supabase 客户端（单例）"""
    global _supabase
    if _supabase is None:
        _supabase = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
    return _supabase


def fetch_opc_profiles() -> List[Dict[str, Any]]:
    """获取所有可用 OPC 画像"""
    client = get_supabase()
    response = (
        client.table("opc_profiles")
        .select("*")
        .eq("is_deleted", False)
        .eq("is_available", True)
        .execute()
    )
    return response.data or []


def fetch_opc_profiles_by_ids(ids: List[str]) -> List[Dict[str, Any]]:
    """根据 ID 列表获取 OPC 画像"""
    if not ids:
        return []
    client = get_supabase()
    response = (
        client.table("opc_profiles")
        .select("*")
        .in_("id", ids)
        .eq("is_deleted", False)
        .execute()
    )
    return response.data or []


def save_demand_profile(profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """保存或更新需求画像（按 session_id 去重）"""
    client = get_supabase()
    # 先查是否存在
    existing = (
        client.table("demand_profiles")
        .select("id")
        .eq("session_id", profile.get("session_id", ""))
        .eq("is_deleted", False)
        .execute()
    )
    if existing.data:
        # 更新
        resp = (
            client.table("demand_profiles")
            .update(profile)
            .eq("id", existing.data[0]["id"])
            .execute()
        )
    else:
        # 插入
        resp = client.table("demand_profiles").insert(profile).execute()
    return resp.data[0] if resp.data else None


def save_conversation_message(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """保存单条对话消息"""
    client = get_supabase()
    resp = client.table("conversation_history").insert(msg).execute()
    return resp.data[0] if resp.data else None
