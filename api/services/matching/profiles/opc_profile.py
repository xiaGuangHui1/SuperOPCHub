"""OPC 能力画像管理 —— 读取 + 缓存 + 索引"""

from typing import List, Dict, Any, Optional
from db.supabase import _get, fetch_opc_profiles
from services.matching.schemas import EnhancedOPCProfile

# 内存缓存
_opc_cache: Optional[List[EnhancedOPCProfile]] = None
_cache_ts: float = 0.0


def get_all_opc_profiles(force_refresh: bool = False) -> List[EnhancedOPCProfile]:
    """
    获取所有 OPC 画像（带缓存，避免重复查询）。

    缓存有效期约 5 分钟。
    """
    global _opc_cache, _cache_ts
    import time

    now = time.time()
    if not force_refresh and _opc_cache is not None and (now - _cache_ts) < 300:
        return _opc_cache

    rows = fetch_opc_profiles()
    profiles = [EnhancedOPCProfile.from_db_row(r) for r in rows]

    _opc_cache = profiles
    _cache_ts = now
    return profiles


def get_opc_by_ids(opc_ids: List[str]) -> List[EnhancedOPCProfile]:
    """根据 ID 列表获取 OPC 画像"""
    all_profiles = get_all_opc_profiles()
    id_set = set(opc_ids)
    return [p for p in all_profiles if p.opc_id in id_set]


def index_opc_by_skill() -> Dict[str, List[str]]:
    """构建技能 → OPC ID 倒排索引"""
    profiles = get_all_opc_profiles()
    index: Dict[str, List[str]] = {}

    for p in profiles:
        for skill_info in p.capabilities.get("primary_skills", []):
            skill = skill_info.get("skill", "") if isinstance(skill_info, dict) else str(skill_info)
            if skill:
                skill_lower = skill.lower()
                if skill_lower not in index:
                    index[skill_lower] = []
                index[skill_lower].append(p.opc_id)

    return index


def index_opc_by_domain() -> Dict[str, List[str]]:
    """构建领域 → OPC ID 倒排索引"""
    profiles = get_all_opc_profiles()
    index: Dict[str, List[str]] = {}

    for p in profiles:
        for domain in p.capabilities.get("domains", []):
            if domain:
                d_lower = domain.lower()
                if d_lower not in index:
                    index[d_lower] = []
                index[d_lower].append(p.opc_id)

        role = p.capabilities.get("domains", [])
        if not role:
            # 从 bio 提取关键词作为领域
            pass

    return index


def clear_opc_cache():
    """清空 OPC 缓存"""
    global _opc_cache, _cache_ts
    _opc_cache = None
    _cache_ts = 0.0
