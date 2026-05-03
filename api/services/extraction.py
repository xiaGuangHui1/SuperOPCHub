"""需求提取服务 —— 通过 LLM 从对话中提取结构化需求画像"""

import json
from typing import List, Dict, Optional
from models.schemas import DemandProfileOut, ChatMessage
from services.llm import chat_completion
from services import prompting


def extract_demand_profile(
    messages: List[ChatMessage],
) -> DemandProfileOut:
    """
    从对话历史中提取结构化的需求画像。

    使用 JSON 模式确保 LLM 返回可解析的结构化数据。
    返回包含完整度信息的 DemandProfileOut。
    """
    system_prompt = prompting.EXTRACTION_SYSTEM
    user_prompt = prompting.build_extraction_prompt(messages)

    raw = chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # fallback: 尝试修复常见 JSON 问题
        try:
            data = json.loads(raw.strip().rstrip(","))
        except json.JSONDecodeError:
            return DemandProfileOut(
                session_id="",
                is_complete=False,
                missing_fields=["无法解析需求"],
            )

    return DemandProfileOut(
        session_id="",
        project_type=data.get("project_type", ""),
        budget_min=data.get("budget_min"),
        budget_max=data.get("budget_max"),
        timeline=data.get("timeline", ""),
        skills_required=data.get("skills_required", []),
        description=data.get("description", ""),
        is_complete=data.get("is_complete", False),
        missing_fields=data.get("missing_fields", []),
    )


def generate_assistant_message(
    messages: List[ChatMessage],
    demand_profile: DemandProfileOut,
) -> str:
    """
    生成 AI 助手的回复消息。

    如果需求不完整，向用户追问缺失信息；
    如果需求完整，告知用户即将开始匹配。
    """
    system_prompt = prompting.CONVERSATION_SYSTEM
    user_prompt = prompting.build_conversation_prompt(messages, demand_profile)

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
