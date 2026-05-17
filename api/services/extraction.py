"""需求提取服务 —— 通过 Instructor 从对话中提取结构化需求画像"""

from typing import List, Optional, Tuple
from models.schemas import DemandProfileOut, ChatMessage, OPCMatch, ExtractionWithReply
from services.llm import chat_completion, structured_completion
from services import prompting


def extract_and_reply(
    messages: List[ChatMessage],
    user_round: int = 1,
) -> Tuple[DemandProfileOut, str]:
    """
    一次 LLM 调用同时完成：需求提取 + AI 回复生成。

    返回 (DemandProfileOut, assistant_message)
    """
    system_prompt = prompting.COMBINED_SYSTEM
    user_prompt = prompting.build_combined_prompt(messages, user_round)

    result = structured_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_model=ExtractionWithReply,
        temperature=0.3,
        max_retries=1,
    )

    profile = DemandProfileOut(
        session_id="",
        project_type=result.project_type,
        description=result.description,
        industry=result.industry,
        skills_required=result.skills_required,
        timeline=result.timeline,
        project_scope=result.project_scope,
        collaboration_mode=result.collaboration_mode,
        service_expectations=result.service_expectations,
        target_users=result.target_users,
        constraints=result.constraints,
        budget_min=result.budget_min,
        budget_max=result.budget_max,
    )
    return profile, result.assistant_message


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
    :param user_round: 当前用户发言轮次（提供给 LLM 作为上下文参考）
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

    profile.session_id = ""
    return profile


def generate_assistant_message(
    messages: List[ChatMessage],
    demand_profile: DemandProfileOut,
    user_round: int = 1,
    matches: Optional[List[OPCMatch]] = None,
) -> str:
    """
    生成 AI 助手的回复消息。

    如果传入了匹配结果，AI 会直接引用匹配到的 OPC 进行推荐。
    """
    system_prompt = prompting.CONVERSATION_SYSTEM
    user_prompt = prompting.build_conversation_prompt(
        messages, demand_profile, user_round, matches
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
