"""嵌入工具 —— 文本相似度计算"""

import math
from typing import List
from services.llm import get_embeddings

# 缓存 OPC 画像的嵌入向量，避免重复调用 API
_embedding_cache: dict = {}


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """计算两个向量的余弦相似度 [0, 1]"""
    dot = sum(ai * bi for ai, bi in zip(a, b))
    na = math.sqrt(sum(ai ** 2 for ai in a))
    nb = math.sqrt(sum(bi ** 2 for bi in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """获取文本嵌入向量（自动缓存）"""
    uncached = []
    uncached_indices = []
    results = [None] * len(texts)

    for i, t in enumerate(texts):
        if t in _embedding_cache:
            results[i] = _embedding_cache[t]
        else:
            uncached.append(t)
            uncached_indices.append(i)

    if uncached:
        embeddings = get_embeddings(uncached)
        for idx, emb in zip(uncached_indices, embeddings):
            _embedding_cache[texts[idx]] = emb
            results[idx] = emb

    return results


def clear_cache():
    """清空嵌入缓存"""
    _embedding_cache.clear()
