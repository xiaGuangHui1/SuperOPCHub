"""需求提取服务 —— 通过 Instructor 从对话中提取结构化需求画像"""

from typing import List
from models.schemas import DemandProfileOut, ChatMessage
from services.llm import chat_completion, structured_completion
from services import prompting


def extract_demand_profile(
    messages: List[ChatMessage],
    user_round: int = 1,
) -> DemandProfileOut:
    """
    通过 Instructor 从对话历史中提取结构化需求画像。

    Instructor 自动处理：
    - JSON Schema 注入
    - Pydantic 字段校验
    - 格式错误自动重试（最多 2 次）

    :param messages:   完整对话历史
    :param user_round: 当前用户发言轮次（用于 3 轮强制收束）
    """
    system_prompt = prompting.EXTRACTION_SYSTEM
    user_prompt = prompting.build_extraction_prompt(messages, user_round)

    profile = structured_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_model=DemandProfileOut,
        temperature=0.1,
        max_retries=2,
    )

    # 第 3 轮强制收束：无视 is_complete，直接标记完整
    if user_round >= 3:
        profile.is_complete = True
        profile.missing_fields = []

    profile.session_id = ""
    return profile


def generate_assistant_message(
    messages: List[ChatMessage],
    demand_profile: DemandProfileOut,
    user_round: int = 1,
) -> str:
    """
    生成 AI 助手的回复消息。

    - 需求不完整 → 追问缺失信息（最多 3 轮）
    - 第 3 轮 → 总结收束，引导匹配
    - 需求完整 → 告知用户即将开始匹配
    """
    system_prompt = prompting.CONVERSATION_SYSTEM
    user_prompt = prompting.build_conversation_prompt(
        messages, demand_profile, user_round
    )

    return chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
        max_tokens=512,
    )


def generate_match_explanation(
    demand: DemandProfileOut,
    opc_name: str,
    opc_role: str,
    opc_skills: List[str],
    opc_description: str,
) -> str:
    """为匹配结果生成简短的解释文本"""
    system_prompt = prompting.MATCH_EXPLANATION_SYSTEM
    user_prompt = prompting.build_match_explanation_prompt(
        demand, opc_name, opc_role, opc_skills, opc_description
    )

    return chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=256,
    )
