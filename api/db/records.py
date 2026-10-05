"""备案池本地存储 —— 用 JSON 文件存网站主主动备案的记录。

本地调试阶段替代 Supabase（Supabase 现在连不上）。
记录格式与 opc_profiles 兼容，可直接喂给 match_opc_profiles 做关键词匹配。
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "records.json"


def _load() -> List[Dict[str, Any]]:
    """读所有备案记录，文件不存在返回空列表"""
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save(records: List[Dict[str, Any]]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def fetch_records() -> List[Dict[str, Any]]:
    """获取所有备案记录（match_opc_profiles 兼容格式）"""
    return _load()


def save_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """追加一条备案记录，返回带 id / created_at 的完整记录"""
    records = _load()
    full = {
        "id": record.get("id") or str(uuid.uuid4()),
        "name": record.get("name", ""),
        "url": record.get("url", ""),
        "role": record.get("role") or "独立开发者",
        "description": record.get("description", ""),
        "skills": record.get("skills", ""),  # 逗号分隔字符串
        "github": record.get("github", ""),
        "avatar_url": None,
        "is_available": True,
        "created_at": record.get("created_at") or datetime.now().isoformat(timespec="seconds"),
    }
    records.append(full)
    _save(records)
    return full
