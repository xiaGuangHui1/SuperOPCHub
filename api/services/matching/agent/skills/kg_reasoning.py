"""Skill B: 知识图谱领域推断 —— 基于知识图谱的链式推理"""

from typing import List, Dict, Any
from services.matching.knowledge.graph import (
    infer_domain_from_keywords,
    infer_from_project_type,
    get_related_skills,
    PROJECT_TYPE_ATTRS,
)


def skill_kg_reasoning(
    user_input: str,
    known_slots: Dict[str, Any],
    missing_dimensions: List[str],
) -> Dict[str, Any]:
    """
    Skill B 主函数：基于知识图谱补全缺失维度。

    推理链：
    1. 从用户输入提取关键词 → 推断领域
    2. 已知项目类型 → 查知识图谱找典型属性
    3. 已知领域 → 推导相关技能
    """
    results = {}

    # Step 1: 从用户原始输入推断领域
    domain_result = infer_domain_from_keywords(user_input)
    if domain_result["confidence"] > 0.3 and "domain" in missing_dimensions:
        results["domain"] = {
            "value": domain_result["value"],
            "confidence": domain_result["confidence"],
            "alternatives": domain_result.get("alternatives", []),
            "source": "knowledge_graph",
        }

    # Step 2: 如果已知项目类型，查知识图谱
    project_type = known_slots.get("project_type") or known_slots.get("primary_need")
    if project_type:
        kg_result = infer_from_project_type(str(project_type))
        if kg_result["confidence"] > 0:
            if "domain" in missing_dimensions and "domain" not in results:
                results["domain"] = {
                    "value": kg_result.get("domain", ""),
                    "confidence": kg_result["confidence"],
                    "alternatives": [],
                    "source": "knowledge_graph",
                }
            if "required_skills" in missing_dimensions:
                results["required_skills"] = {
                    "value": kg_result.get("skills", []),
                    "confidence": kg_result["confidence"],
                    "alternatives": [],
                    "source": "knowledge_graph",
                }
            if "estimated_budget_range" in missing_dimensions:
                budget = kg_result.get("budget", {})
                results["estimated_budget_range"] = {
                    "value": budget,
                    "confidence": kg_result["confidence"],
                    "alternatives": [],
                    "source": "knowledge_graph",
                }
            if "timeline" in missing_dimensions:
                results["timeline"] = {
                    "value": kg_result.get("timeline", ""),
                    "confidence": kg_result["confidence"],
                    "alternatives": [],
                    "source": "knowledge_graph",
                }
            if "complexity" in missing_dimensions:
                results["complexity"] = {
                    "value": kg_result.get("complexity", "medium"),
                    "confidence": kg_result["confidence"],
                    "alternatives": [],
                    "source": "knowledge_graph",
                }

    # Step 3: 已知领域 → 推导相关技能
    domain = known_slots.get("domain") or (results.get("domain", {}).get("value"))
    if domain and "required_skills" in missing_dimensions and "required_skills" not in results:
        related = get_related_skills(str(domain), str(project_type or ""))
        if related:
            results["required_skills"] = {
                "value": related[:5],
                "confidence": 0.55,
                "alternatives": [],
                "source": "knowledge_graph",
            }

    return results
