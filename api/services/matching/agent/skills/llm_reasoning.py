"""Skill D: LLM 推理填充 —— 当其他 Skill 无法补全时用 LLM 常识推理兜底"""

import json
from typing import List, Dict, Any
from services.llm import chat_completion


REASONING_SYSTEM = """你是需求分析专家，需要根据用户的只言片语和已收集的信息，推理补全缺失的需求维度。

【要求】
1. 每个推断都要有明确的推理依据（基于已知信息的逻辑推导）
2. 给出置信度（0-1），表示对推断的确信程度
3. 确实无法推断的维度填 "NEED_CLARIFY"
4. 不要编造信息

【输出格式】
必须是合法的 JSON：
{
  "dimensions": {
    "primary_need": {"value": "...", "confidence": 0.8, "reasoning": "因为用户提到了..."},
    "required_skills": {"value": ["技能1", "技能2"], "confidence": 0.7, "reasoning": "..."},
    ...
  }
}"""


def skill_llm_reasoning(
    vague_input: str,
    collected_info: Dict[str, Any],
    still_missing: List[str],
    behavioral_signals: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Skill D 主函数：LLM 常识推理填充。

    :param vague_input: 用户原始输入
    :param collected_info: 已收集到的信息（来自其他 Skill）
    :param still_missing: 仍然缺失的维度列表
    :param behavioral_signals: 用户行为信号（可选）
    """

    # 构建已收集信息的可读文本
    collected_text = ""
    for dim, info in collected_info.items():
        val = info.get("value", info) if isinstance(info, dict) else info
        conf = info.get("confidence", "?") if isinstance(info, dict) else "?"
        src = info.get("source", "unknown") if isinstance(info, dict) else "unknown"
        collected_text += f"  - {dim}: {val} (置信度={conf}, 来源={src})\n"

    # 行为信号（如果有的话）
    behavior_hint = ""
    if behavioral_signals:
        searches = behavioral_signals.get("search_queries", [])
        if searches:
            behavior_hint += f"\n用户搜索记录：{'、'.join(searches)}"
        cats = behavioral_signals.get("time_spent_categories", {})
        if cats:
            top_cat = max(cats, key=cats.get)
            behavior_hint += f"\n用户浏览偏好：{top_cat} 类内容浏览时间最长"

    prompt = f"""【用户的原始输入】
{vague_input}

【已从历史数据和知识库收集的信息】
{collected_text}
{behavior_hint}

【仍然缺失、需要你推理的维度】
{'、'.join(still_missing)}

请推理补全以上缺失维度，输出 JSON。"""

    try:
        resp = chat_completion(
            messages=[
                {"role": "system", "content": REASONING_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=1024,
        )
        # 尝试提取 JSON
        resp = resp.strip()
        if resp.startswith("```"):
            # 去掉 markdown 代码块标记
            lines = resp.split("\n")
            resp = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])

        data = json.loads(resp)
        dimensions = data.get("dimensions", {})

        # 转换为标准格式
        results = {}
        for dim, info in dimensions.items():
            if info.get("value") == "NEED_CLARIFY" or not info.get("value"):
                results[dim] = {
                    "value": [],
                    "confidence": 0.0,
                    "alternatives": [],
                    "source": "LLM_reasoning",
                    "reasoning": info.get("reasoning", ""),
                }
            else:
                results[dim] = {
                    "value": info.get("value"),
                    "confidence": min(0.7, info.get("confidence", 0.5)),
                    "alternatives": info.get("alternatives", []),
                    "source": "LLM_reasoning",
                    "reasoning": info.get("reasoning", ""),
                }

        return results

    except (json.JSONDecodeError, Exception):
        # LLM 调用失败或解析失败，返回空结果
        empty = {}
        for dim in still_missing:
            empty[dim] = {
                "value": [],
                "confidence": 0.0,
                "alternatives": [],
                "source": "LLM_reasoning_failed",
                "reasoning": "",
            }
        return empty
