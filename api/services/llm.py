"""LLM 客户端 —— 封装 OpenAI 兼容 API 调用"""

from typing import List, Dict, Any, Optional
from openai import OpenAI

from config import config

_client: Optional[OpenAI] = None
_embedding_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)
    return _client


def get_embedding_client() -> OpenAI:
    """获取 Embedding 专用客户端（支持独立 API 配置）"""
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = OpenAI(
            api_key=config.EMBEDDING_API_KEY,
            base_url=config.EMBEDDING_BASE_URL,
        )
    return _embedding_client


def chat_completion(
    messages: List[Dict[str, str]],
    temperature: float = 0.3,
    max_tokens: int = 1024,
    response_format: Optional[Dict[str, Any]] = None,
) -> str:
    """
    调用 LLM 聊天接口，返回文本内容。

    :param messages:        标准 conversation 格式 [{"role":"user","content":"..."}]
    :param temperature:     生成随机度
    :param max_tokens:      最大输出 token
    :param response_format: 结构化输出格式（如 {"type":"json_object"}）
    """
    client = get_client()
    kwargs: Dict[str, Any] = {
        "model": config.LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format:
        kwargs["response_format"] = response_format

    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    获取文本嵌入向量（批量）

    :param texts: 文本列表
    :return:      嵌入向量列表，每个是 float 数组
    """
    client = get_embedding_client()
    resp = client.embeddings.create(model=config.EMBEDDING_MODEL, input=texts)
    # 按输入顺序返回
    return [item.embedding for item in resp.data]
