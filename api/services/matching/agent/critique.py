"""LLM Self-Critique —— 对推理结果做质量审核"""

import json
from typing import Dict, Any
from services.llm import chat_completion


CRITIQUE_SYSTEM = """你是需求分析质检专家。请检查以下需求推断的合理性。

逐条评估：
1. 每条推断在逻辑上是否合理？
2. 是否存在自相矛盾？
3. 是否有被忽略的重要可能性？
4. 哪些推断有数据支撑，哪些只是猜测？

【输出格式】
{
  "critiques": [
    {
      "dimension": "维度名",
      "current_value": "当前值",
      "current_confidence": 0.8,
      "issue": "存在问题描述（无问题填 'OK'）",
      "suggestion": "改进建议",
      "adjusted_confidence": 0.7
    }
  ],
  "overall_assessment": "整体评估",
  "adjustments": {
    "维度名": 0.7
  }
}"""


def self_critique(
    vague_input: str,
    requirement_pool: Dict[str, Any],
) -> Dict[str, Any]:
    """
    LLM Self-Critique：对推理结果做最终质量审核。

    返回：置信度调整建议
    """
    # 构建需求池摘要
    summary_lines = []
    for dim, info in sorted(requirement_pool.items()):
        val = info.get("value") if isinstance(info, dict) else info
        conf = info.get("confidence", 0.0) if isinstance(info, dict) else 0.0
        src = info.get("sources", ["?"]) if isinstance(info, dict) else ["?"]
        summary_lines.append(f"  {dim}: {val} (置信度={conf}, 来源={src})")

    summary = "\n".join(summary_lines)
    prompt = f"""【用户原始输入】
{vague_input}

【系统推断结果】
{summary}"""

    try:
        resp = chat_completion(
            messages=[
                {"role": "system", "content": CRITIQUE_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=1024,
        )
        resp = resp.strip()
        if resp.startswith("```"):
            lines = resp.split("\n")
            resp = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])

        data = json.loads(resp)
        return data

    except (json.JSONDecodeError, Exception):
        return {
            "critiques": [],
            "overall_assessment": "无法完成 Self-Critique",
            "adjustments": {},
        }


def apply_critique_adjustments(
    pool: Dict[str, Any],
    critique_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    将 Self-Critique 的置信度调整应用到需求池。
    """
    adjustments = critique_result.get("adjustments", {})
    adjusted = dict(pool)

    for dim, new_conf in adjustments.items():
        if dim in adjusted and isinstance(adjusted[dim], dict):
            old_conf = adjusted[dim].get("confidence", 0.0)
            # 取加权平均（原置信度权重 0.6，critique 调整 0.4）
            adjusted[dim]["confidence"] = round(old_conf * 0.6 + new_conf * 0.4, 3)
            adjusted[dim]["critiqued"] = True

    return adjusted
