"""画像向量管理 —— 生成 + 缓存 + 更新"""

from typing import List
from services.llm import get_embeddings
from services import embedding as embed_utils


def generate_demand_embedding(
    primary_need: str,
    domain: str,
    skills: List[str],
    description: str = "",
) -> List[float]:
    """生成需求画像的向量表示"""
    parts = [primary_need, domain, description] + skills
    text = " ".join(p for p in parts if p)
    if not text.strip():
        return [0.0] * 1024
    embeddings = embed_utils.embed_texts([text])
    return embeddings[0] if embeddings else [0.0] * 1024


def generate_opc_embedding(
    bio: str,
    skills: List[str],
    domains: List[str],
) -> List[float]:
    """生成 OPC 画像的向量表示"""
    parts = [bio] + skills + domains
    text = " ".join(p for p in parts if p)
    if not text.strip():
        return [0.0] * 1024
    embeddings = embed_utils.embed_texts([text])
    return embeddings[0] if embeddings else [0.0] * 1024
