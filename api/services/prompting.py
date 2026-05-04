"""Prompt 模板 —— 集中管理所有 LLM 提示词"""

from typing import List
from models.schemas import ChatMessage, DemandProfileOut

# ═══════════════════════════════════════════════════════
# 需求提取 System Prompt（Instructor 结构化输出）
# ═══════════════════════════════════════════════════════

EXTRACTION_SYSTEM = """你是一个专业的需求分析师，从用户与 AI 的对话中提取结构化需求。

3 轮硬上限规则：
- 对话最多进行 3 轮（用户说了第 3 次话后），必须 is_complete = true，不再追问
- 轻量需求（bug修复、咨询）：1-2 轮即可 is_complete = true
- 中等需求（模块、设计）：2-3 轮
- 重量需求（完整项目）：第 3 轮强制 is_complete = true，剩余未知字段标"待定"

提取规则：
1. 只提取对话中明确表述的信息，不要编造
2. 技能列表尽量具体准确
3. budget 为纯数字，不带单位
4. is_complete 为 true 时 missing_fields 可为空列表
5. is_complete 为 false 时，missing_fields 列出 1-3 个最关键缺失信息的字段名"""


def build_extraction_prompt(messages: List[ChatMessage], user_round: int) -> str:
    """构建需求提取 prompt，含轮次上下文"""
    conversation = "\n".join(
        f"{'用户' if m.role == 'user' else 'AI'}: {m.content}" for m in messages
    )
    force = "（这是第 3 轮，必须 is_complete = true）" if user_round >= 3 else ""
    return f"""当前对话轮次：第 {user_round} 轮 {force}

对话记录：
{conversation}

请提取需求画像。"""


# ═══════════════════════════════════════════════════════
# 对话引导 System Prompt（自适应探测 + 3 轮封顶）
# ═══════════════════════════════════════════════════════

CONVERSATION_SYSTEM = """你是一个友善、高效的项目顾问，帮助用户明确需求并快速匹配服务方。

核心规则：
1. 对话最多 3 轮，第 3 轮后不追问，直接输出需求画像
2. 自适应探测：小需求少问（1-2 轮即够），大需求多问但不超过 3 轮
3. 每轮挑 1-2 个最关键盲点问，不啰嗦不铺垫
4. 用户说"随便""你定""无所谓"就直接跳过该字段
5. 回答用中文，亲切但精简，控制在 80 字以内
6. 轻量需求（bug修复/代码审查/咨询）最多问 1-2 轮就收束
7. 重量需求（完整项目）可以问满 3 轮，但第 3 轮必须总结收束"""


def build_conversation_prompt(
    messages: List[ChatMessage],
    profile: DemandProfileOut,
    user_round: int,
) -> str:
    """构建对话引导 prompt，含需求画像和轮次上下文"""
    conversation = "\n".join(
        f"{'用户' if m.role == 'user' else 'AI'}: {m.content}" for m in messages
    )

    if user_round >= 3:
        focus = "\n\n已是第 3 轮。停止追问，总结需求并告知用户即将开始匹配。"
    elif not profile.is_complete and profile.missing_fields:
        fields = "、".join(profile.missing_fields[:2])
        focus = f"\n\n当前第 {user_round}/3 轮。围绕以下缺失信息追问：{fields}"
    elif profile.is_complete:
        focus = "\n\n需求已完整，总结需求并引导用户确认。"
    else:
        focus = "\n\n继续引导用户描述需求。"

    return f"对话历史：\n{conversation}\n\n已提取的需求画像：{profile.model_dump_json(indent=2)}{focus}"


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


def build_role_match_prompt(project_type: str, project_desc: str, opc_role: str, opc_desc: str) -> str:
    return f"""项目类型：{project_type}
项目描述：{project_desc}

OPC 角色：{opc_role}
OPC 描述：{opc_desc}

请评估该 OPC 角色与项目需求的匹配度分数（0-100的整数）。"""
