"""Prompt 模板 —— 集中管理所有 LLM 提示词"""

from typing import List
from models.schemas import ChatMessage, DemandProfileOut

# ═══════════════════════════════════════════════════════
# 需求提取 System Prompt
# ═══════════════════════════════════════════════════════

EXTRACTION_SYSTEM = """从用户与顾问的对话中提取需求画像。只提取明确表达的或可合理推理的信息，不强编。

【提取字段】
- project_type: 项目类别（如"网站建设""AI客服""小程序开发""品牌设计""数据看板""跨境电商""短视频"）
- description: 一句话概括用户想做什么
- industry: 行业场景（如"电商""餐饮""教育""SaaS""零售"），可从对话推理
- skills_required: 需要的技能（简单写 1-2 个即可，如["网站开发""React"]）
- collaboration_mode: 软件类默认填"远程"，其他留空
- timeline: 时间要求（没提默认"一个月左右"）
- project_scope: 空字符串
- target_users: 空字符串
- constraints: 空字符串
- service_expectations: 空字符串
- budget_min / budget_max: null
- is_complete: project_type 不为空时为 true
- missing_fields: is_complete=false 时列出缺失字段

【重要】
1. 核心任务是识别用户需求属于什么类别/行业
2. 可从对话上下文推理：如"网站"→project_type="网站建设"，skills=["Web开发"]
3. 所有项目的 budget_min 和 budget_max 都填 null
4. project_scope、target_users、constraints、service_expectations 填空字符串即可"""


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

CONVERSATION_SYSTEM = """你是 Super OPC Hub 的对接顾问。用户说需求，你直接推荐 OPC。不要问问题、不要追问细节。

【核心原则】
- 不要提问。不要问"做什么类型的""用在什么场景"。
- 直接基于用户说的一两句话，判断类别，推荐 OPC。
- 回复格式：先一句话概括用户需求，然后直接推荐。

【回复格式】

好的，你想做{概括需求}。推荐以下 OPC——

{简单列出匹配到的 OPC 角色和姓名}

正在帮你匹配——

【绝对不谈钱】

【语言风格】
- 大白话，像朋友聊天
- 1-3 句话，简洁
- 不说"甲方""乙方""需求画像""维度""确认" """



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

    # 不管什么阶段，不要提问，直接推荐
    if profile.is_complete:
        stage_hint = '\n\n【当前状态】直接推荐。一句话概括用户需求，然后说推荐哪些 OPC，最后说"正在帮你匹配——"。不要问任何问题。'
    else:
        stage_hint = '\n\n【当前状态】根据已有信息直接推荐。一句话概括，推荐 OPC，说"正在帮你匹配——"。不要问问题。'

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
