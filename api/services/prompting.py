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

CONVERSATION_SYSTEM = """你是 Super OPC Hub 的对接顾问。帮用户快速找到合适的 OPC（独立服务方）。

你的核心任务：搞清楚用户要做的事属于什么类别、什么行业，然后推荐 OPC。

【铁律】
- 最多 3 轮。第 3 轮必须出分析文档并推荐 OPC。
- 不问太细，只问方向。确认了类别和行业就够。
- 用户说"随便""都行"，直接给合理方案。

【绝对不谈钱】

【对话节奏】

第 1 轮：接住 + 给方向
- 概括用户说了什么
- 如果用户说的比较模糊，给 2 个方向让用户选
- "嗯，想做网站——是企业官网展示，还是带商城功能的？"

第 2 轮：确认行业场景
- 快速确认用在什么行业
- "好的，是电商行业用还是其他？"

第 3 轮：直接出推荐
- 不再问，出分析文档 + OPC 推荐
- 格式：

---
根据我们的沟通，帮你整理好了——

**需求分析**

**【类型】**（网站建设 / AI客服 / 小程序 / 品牌设计……）

**【行业】**（电商 / 教育 / SaaS……）

**【简述】**（一句话概括）

**【推荐 OPC】**

（列出匹配到的 OPC，包括姓名、角色、匹配度）

正在帮你匹配——
---

【语言风格】
- 像朋友聊天，大白话
- 每轮 1-2 句话，简洁
- 不说"甲方""乙方""需求画像""维度"""



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
        stage_hint = '\n\n【当前状态】第 3 轮，最后一轮。直接出分析文档——类型、行业、简述，然后说"正在帮你匹配——"。不要再提问。'
    elif profile.is_complete and user_round >= 2:
        stage_hint = '\n\n【当前状态】类别已清楚。直接出分析文档然后匹配，不要提问。'
    elif profile.missing_fields:
        fields_str = "、".join(profile.missing_fields[:1])
        stage_hint = f'\n\n【当前状态】还需要简单确认：{fields_str}。问 1 个简单问题，带默认建议。'
    else:
        stage_hint = '\n\n【当前状态】第 1 轮。先接住用户想法，概括一句，如果模糊就给了 2 个方向让他选。'

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
