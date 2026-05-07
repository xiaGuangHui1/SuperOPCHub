"""Skill C: 统计模式匹配 —— 基于关联规则和贝叶斯推断"""

from typing import List, Dict, Any
from services.matching.knowledge.rules import match_rules, bayesian_predict


ALL_SLOTS = [
    "primary_need", "domain", "required_skills", "complexity",
    "estimated_budget_range", "timeline", "industry", "constraints", "description"
]


def skill_statistical_inference(
    known_slots: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Skill C 主函数：基于关联规则和贝叶斯推断补全未知维度。

    1. 关联规则匹配：从已知字段找到最相关的规则
    2. 贝叶斯推断：对规则未覆盖的维度使用先验分布
    """
    # 构建已知字段的简单映射（只取字符串类型的值用于规则匹配）
    simple_known = {}
    for k, v in known_slots.items():
        if isinstance(v, str):
            simple_known[k] = v
        elif isinstance(v, dict) and "value" in v:
            val = v.get("value")
            if isinstance(val, str):
                simple_known[k] = val

    results = {}

    # 1. 关联规则匹配
    matched_rules = match_rules(simple_known)
    for rule in matched_rules:
        consequent = rule["consequent"]
        for slot_name, slot_value in consequent.items():
            if slot_name in results:
                continue  # 已匹配到更高置信度的规则
            results[slot_name] = {
                "value": slot_value,
                "confidence": rule["confidence"],
                "source": "association_rule",
                "lift": rule["lift"],
            }

    # 2. 贝叶斯推断补充未覆盖维度
    for slot in ALL_SLOTS:
        if slot in simple_known or slot in results:
            continue
        pred = bayesian_predict(slot, simple_known)
        if pred["confidence"] > 0.0:
            results[slot] = pred

    return results
