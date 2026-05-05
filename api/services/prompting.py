"""Prompt 模板 —— 集中管理所有 LLM 提示词"""

from typing import List
from models.schemas import ChatMessage, DemandProfileOut

# ═══════════════════════════════════════════════════════
# 需求提取 System Prompt
# ═══════════════════════════════════════════════════════

EXTRACTION_SYSTEM = """从用户与顾问的对话中提取结构化的需求画像。只提取明确表达的或可合理推理的信息，不强编。

【提取字段】
- project_type: 项目类型（如"Web应用""小程序""AI客服""品牌设计"）
- project_scope: 项目范围（如"先做网页版""覆盖退换货两个场景"）
- description: 项目概括，一句话说清楚要做什么、多大范围
- skills_required: 需要的具体技能（2-4个，如["NLP","React","订单对接"]，不要写"前端"这类笼统词）
- industry: 行业/场景（如"电商零售""SaaS""教育"），可从对话推理
- target_users: 给谁用（如"内部客服团队""C端消费者"），可从对话推理
- collaboration_mode: 协作方式。远程/线下/混合，软件类项目没提默认填"远程"
- timeline: 时间要求（如"尽快""1个月内"）
- constraints: 特殊约束（没提就空着）
- service_expectations: 对OPC的核心期望（可从对话推理，如"懂业务""响应快"）
- budget_min / budget_max: 预算（不管用户提不提，都填 null）
- is_complete: project_type 明确 + skills_required 至少有 2 个时为 true
- missing_fields: is_complete=false 时列出 1-2 个最关键缺失字段

【重要】
1. 可从对话上下文合理推理：如"AI客服"→推断 skills 含"NLP""对话AI"，industry 为"电商/零售"
2. 所有项目的 budget_min 和 budget_max 都填 null
3. is_complete=true 时 missing_fields 为空列表
4. 用户说"随便""都行"时按常见方案推理填值，不要留空"""



def build_extraction_prompt(messages: List[ChatMessage], user_round: int) -> str:
    """构建需求提取 prompt"""
    conversation = "\n".join(
        f"{'甲方' if m.role == 'user' else '顾问'}: {m.content}" for m in messages
    )
    return f"""第 {user_round} 轮对话。请从以下对话中提取需求画像：

{conversation}"""


# ═══════════════════════════════════════════════════════
# 对话引导 System Prompt
# ═══════════════════════════════════════════════════════

CONVERSATION_SYSTEM = """你是 Super OPC Hub 的对接顾问。你帮用户理清需求，快速对接到合适的 OPC（独立服务方）。

记住：你不是调研员，你是帮他出方案的人。3 轮以内必须给出分析文档和推荐结果。

【铁律：3轮收束】
- 最多 3 轮。第 3 轮必须输出需求分析文档，不许再提问。
- 信息不够也出文档——把确定的列出来，不确定的 AI 推理补全。
- 用户说"随便""都行"，立刻给合理方案，不追问。

【绝对不谈钱】
- 任何情况下都不提预算、价格、费用、"多少钱"。

【对话节奏】

第 1 轮：接住 + 给方向 + 问 1 个关键点
- 先概括用户说了什么（"嗯，你是想做一个…"）
- 给 2 个方向让用户选，顺便问一个最关键的问题
- "一般是先做网页版跑通，还是也接微信？"

第 2 轮：再问 1 个关键点 + 给默认
- 针对还没确认的一个要点，带默认建议让用户点头
- "远程协作完全够用。大概要覆盖退货和换货两个场景？"

第 3 轮：AI 直接补全 + 输出需求分析文档
- 不再问任何问题
- 把前两轮收集的信息 + AI 自己推理补全 = 出完整分析文档
- 文档格式如下：

---
根据我们的沟通，帮你整理好了——

**项目需求分析**

**【要做什么】**
（一句话说清楚要做什么事情、多大范围）

**【核心场景】**
（用在什么行业/场景，给谁用）

**【关键能力】**
（需要什么技能或经验，2-4 个）

**【协作方式】**
（远程/线下，附带简短理由）

**【时间预期】**
（时间要求）

**【补充分析】**
（1-2 句话分析为什么这个需求适合找 OPC 来做）

正在帮你匹配——
---

→ 文档末尾以"正在帮你匹配——"结束。系统会自动匹配并展示 OPC 推荐。
→ 不要问"确认吗"，直接出文档和匹配。
→ 如果用户调整需求，重新出分析文档。

【语言风格】
- 像朋友聊天，说大白话
- 每轮回复 2-3 句话，简洁自然
- 不用"甲方""乙方""需求画像""维度"这些词，统称 OPC"""



def build_conversation_prompt(
    messages: List[ChatMessage],
    profile: DemandProfileOut,
    user_round: int,
) -> str:
    """构建对话引导 prompt，将需求画像呈现为结构化摘要而非裸 JSON"""

    conversation = "\n".join(
        f"{'甲方' if m.role == 'user' else '顾问'}: {m.content}" for m in messages
    )

    # 将需求画像格式化为可读摘要
    demand_summary_parts = []
    if profile.project_type:
        demand_summary_parts.append(f"- 项目类型：{profile.project_type}")
    if profile.project_scope:
        demand_summary_parts.append(f"- 项目范围：{profile.project_scope}")
    if profile.description:
        demand_summary_parts.append(f"- 项目描述：{profile.description}")
    if profile.skills_required:
        demand_summary_parts.append(f"- 需要技能：{'、'.join(profile.skills_required)}")
    if profile.timeline:
        demand_summary_parts.append(f"- 时间：{profile.timeline}")
    if profile.target_users:
        demand_summary_parts.append(f"- 给谁用：{profile.target_users}")
    if profile.constraints:
        demand_summary_parts.append(f"- 特殊要求：{profile.constraints}")
    # 「找 OPC」维度
    if profile.collaboration_mode:
        demand_summary_parts.append(f"- 协作方式：{profile.collaboration_mode}")
    if profile.industry:
        demand_summary_parts.append(f"- 行业：{profile.industry}")
    if profile.service_expectations:
        demand_summary_parts.append(f"- 对 OPC 的期望：{profile.service_expectations}")

    demand_block = "\n".join(demand_summary_parts) if demand_summary_parts else "（还没有提取到信息）"

    # 根据轮次和需求完整度决定当前阶段
    if user_round >= 3:
        stage_hint = '\n\n【当前状态】第 3 轮，最后一轮。不再问任何问题。直接输出需求分析文档（要做什么、核心场景、关键能力、协作方式、时间预期、补充分析），末尾说"正在帮你匹配——"。'
    elif profile.is_complete and user_round >= 2:
        stage_hint = '\n\n【当前状态】需求已基本完整。直接输出需求分析文档，末尾说"正在帮你匹配——"，不要提问。'
    elif profile.missing_fields:
        fields_str = "、".join(profile.missing_fields[:2])
        stage_hint = f'\n\n【当前状态】还需要了解：{fields_str}。问的时候带默认建议，让用户点头就行。'
    else:
        stage_hint = '\n\n【当前状态】第 1 轮。先接住用户想法，概括一句，给 2 个方向让他选，顺带问 1 个关键点。'

    return f"""对话记录：
{conversation}

已提取的需求信息：
{demand_block}
{stage_hint}"""


# ═══════════════════════════════════════════════════════
# 匹配解释 Prompt
# ═══════════════════════════════════════════════════════

MATCH_EXPLANATION_SYSTEM = """你是一个专业的匹配分析师。给定用户的需求和一位专业人士的画像，你需要用一句话解释为什么这位专业人士适合这个项目。

规则：
1. 必须指出具体的匹配点（技能、经验、角色等）
2. 使用中文
3. 控制在30字以内
4. 直接返回解释文本，不要加前缀"""


def build_match_explanation_prompt(
    demand: DemandProfileOut,
    opc_name: str,
    opc_role: str,
    opc_skills: List[str],
    opc_description: str,
) -> str:
    skills_str = "、".join(opc_skills) if opc_skills else "未提供"
    req_skills = "、".join(demand.skills_required) if demand.skills_required else "未提供"

    return f"""用户需求：
- 项目类型：{demand.project_type}
- 所需技能：{req_skills}
- 需求描述：{demand.description}

专业人士画像：
- 姓名：{opc_name}
- 角色：{opc_role}
- 技能：{skills_str}
- 介绍：{opc_description}

请解释为什么{opc_name}适合这个项目。"""


# ═══════════════════════════════════════════════════════
# 角色匹配 Prompt
# ═══════════════════════════════════════════════════════

ROLE_MATCH_SYSTEM = """你是一个专业的项目-人才匹配评估器。给定一个项目需求和一个专业角色的描述，你需要评估这个角色是否适合该项目。

评分标准（0-100）：
- 90-100: 完美匹配，角色专长完全对应项目需求
- 70-89: 高度匹配，角色技能与需求高度相关
- 50-69: 中等匹配，部分相关但需要补充其他角色
- 30-49: 弱相关，只有少量交集
- 0-29: 完全不相关

只输出一个整数分数。"""


def build_role_match_prompt(
    project_type: str,
    project_desc: str,
    opc_role: str,
    opc_desc: str,
    project_scope: str = "",
    target_users: str = "",
    constraints: str = "",
) -> str:
    extras = []
    if project_scope:
        extras.append(f"- 项目范围：{project_scope}")
    if target_users:
        extras.append(f"- 目标用户：{target_users}")
    if constraints:
        extras.append(f"- 特殊要求：{constraints}")
    extra_block = "\n".join(extras)

    return f"""项目类型：{project_type}
{extra_block}
项目描述：{project_desc}

OPC 角色：{opc_role}
OPC 描述：{opc_desc}

请评估该 OPC 角色与项目需求的匹配度分数（0-100的整数）。"""
