"""全局配置：从环境变量读取，支持 .env 文件"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # LLM 配置（兼容 OpenAI API 及任何兼容接口）
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")

    # Embedding 配置（可选独立配置，默认与 LLM 共用）
    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", LLM_API_KEY)
    EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", LLM_BASE_URL)
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Supabase 配置
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

    # 匹配参数
    MATCH_TOP_K = int(os.getenv("MATCH_TOP_K", "8"))
    MATCH_MIN_SCORE = float(os.getenv("MATCH_MIN_SCORE", "0.0"))


config = Config()
