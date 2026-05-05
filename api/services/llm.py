"""LLM 客户端 —— 封装 OpenAI 兼容 API 调用"""

from typing import List, Dict, Any, Optional, Type, TypeVar
from openai import OpenAI
from pydantic import BaseModel
import instructor

from config import config

_client: Optional[OpenAI] = None
_embedding_client: Optional[OpenAI] = None
_instructor_client: Optional[instructor.Instructor] = None

T = TypeVar("T", bound=BaseModel)


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


def get_instructor_client() -> instructor.Instructor:
    """获取 Instructor 客户端 —— 用于结构化输出"""
    global _instructor_client
    if _instructor_client is None:
        _instructor_client = instructor.from_openai(get_client())
    return _instructor_client


def chat_completion(
    messages: List[Dict[str, str]],
    temperature: float = 0.3,
    max_tokens: int = 1024,
    response_format: Optional[Dict[str, Any]] = None,
) -> str:
    """
    调用 LLM 聊天接口，返回文本内容。
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


def structured_completion(
    messages: List[Dict[str, str]],
    response_model: Type[T],
    temperature: float = 0.1,
    max_tokens: int = 1024,
    max_retries: int = 2,
) -> T:
    """
    调用 LLM 并返回结构化 Pydantic 对象。

    通过 Instructor 自动处理 JSON schema 注入、校验和重试。
    """
    client = get_instructor_client()
    return client.chat.completions.create(
        model=config.LLM_MODEL,
        response_model=response_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        max_retries=max_retries,
    )


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    获取文本嵌入向量（批量）

    自动过滤空字符串 —— SiliconFlow 等 API 不接受空输入。
    """
    client = get_embedding_client()

    # 过滤空字符串：API 不接受空输入
    non_empty = [t for t in texts if t and t.strip()]
    if non_empty:
        resp = client.embeddings.create(model=config.EMBEDDING_MODEL, input=non_empty)
        embeddings_map = {}
        for text, item in zip(non_empty, resp.data):
            embeddings_map[text] = item.embedding
    else:
        embeddings_map = {}

    # 保持输出顺序与输入一致，空字符串返回零向量
    zero_vec = None
    results = []
    for t in texts:
        if t in embeddings_map:
            results.append(embeddings_map[t])
        else:
            if zero_vec is None:
                zero_vec = [0.0] * 1024
            results.append(zero_vec)

    return results
