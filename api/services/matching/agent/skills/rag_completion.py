"""Skill A: RAG 历史需求检索 —— 从历史需求库中检索相似案例"""

from typing import List, Dict, Any, Optional
from services.llm import get_embeddings
from db.supabase import _get


def rag_search(
    query: str,
    top_k: int = 20,
    table: str = "demand_profiles",
) -> List[Dict[str, Any]]:
    """
    从历史需求库中向量检索相似案例。

    当前实现：获取全量历史需求，本地计算相似度。
    后续可升级为 pgvector 或 ChromaDB 方案。
    """
    try:
        rows = _get(
            table,
            params={
                "select": "id,session_id,project_type,description,industry,skills_required,timeline,budget_min,budget_max",
                "is_deleted": "eq.false",
                "order": "created_at.desc",
                "limit": "200",
            },
        )
    except Exception:
        return []

    if not rows:
        return []

    if not query.strip():
        return rows[:top_k]

    # 构建历史文本
    texts = []
    for r in rows:
        parts = []
        if r.get("project_type"):
            parts.append(r["project_type"])
        if r.get("description"):
            parts.append(r["description"])
        if r.get("industry"):
            parts.append(r["industry"])
        texts.append(" ".join(parts) if parts else "")

    query_emb = get_embeddings([query])
    if not query_emb or not query_emb[0]:
        return rows[:top_k]

    text_embs = get_embeddings(texts)
    if not text_embs:
        return rows[:top_k]

    # 计算余弦相似度
    import math

    def cosine(a, b):
        dot = sum(ai * bi for ai, bi in zip(a, b))
        na = math.sqrt(sum(ai ** 2 for ai in a))
        nb = math.sqrt(sum(bi ** 2 for bi in b))
        return dot / (na * nb) if na and nb else 0.0

    q = query_emb[0]
    scored = []
    for i, row in enumerate(rows):
        if text_embs[i] and sum(abs(v) for v in text_embs[i]) > 0:
            sim = cosine(q, text_embs[i])
            scored.append((row, sim))
        else:
            scored.append((row, 0.0))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [row for row, _ in scored[:top_k]]


def aggregate_distribution(
    cases: List[Dict[str, Any]],
    dimension: str,
) -> List[Any]:
    """
    统计相似案例中某维度的值分布。
    返回 [(value, frequency), ...] 按频率降序。
    """
    from collections import Counter

    values = []
    dim_map = {
        "primary_need": "project_type",
        "domain": "industry",
        "industry": "industry",
        "required_skills": "skills_required",
        "timeline": "timeline",
    }
    col = dim_map.get(dimension, dimension)

    for c in cases:
        val = c.get(col)
        if val:
            if isinstance(val, str) and "," in val:
                # 技能类字段拆分
                values.extend(s.strip() for s in val.split(",") if s.strip())
            elif val:
                values.append(val)

    if not values:
        return []

    counter = Counter(values)
    total = sum(counter.values())
    return [({"name": k, "frequency": round(v / total, 3)}) for k, v in counter.most_common(20)]


def skill_rag_completion(
    vague_input: str,
    missing_dimensions: List[str],
) -> Dict[str, Any]:
    """
    Skill A 主函数：从历史需求中补全缺失维度。

    返回格式：
    {
        "dim_name": {
            "value": ...,
            "confidence": ...,
            "alternatives": [...],
            "source": "RAG_historical",
            "supporting_case_ids": [...]
        }
    }
    """
    similar_cases = rag_search(vague_input, top_k=50)

    results = {}
    for dim in missing_dimensions:
        distribution = aggregate_distribution(similar_cases, dim)
        if not distribution:
            results[dim] = {
                "value": "",
                "confidence": 0.0,
                "alternatives": [],
                "source": "RAG_historical",
                "supporting_case_ids": [],
            }
            continue

        top = distribution[0]
        value = top["name"]
        freq = top["frequency"]

        # 找到支撑案例
        dim_map = {"primary_need": "project_type", "domain": "industry", "industry": "industry",
                    "required_skills": "skills_required", "timeline": "timeline"}
        col = dim_map.get(dim, dim)

        supporting = [
            c.get("id") for c in similar_cases
            if str(c.get(col, "")).find(str(value)) >= 0
        ][:3]

        results[dim] = {
            "value": value,
            "confidence": min(0.8, freq),
            "alternatives": [a["name"] for a in distribution[1:4]],
            "source": "RAG_historical",
            "supporting_case_ids": supporting,
        }

    return results
