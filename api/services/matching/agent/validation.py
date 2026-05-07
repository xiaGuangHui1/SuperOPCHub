"""交叉验证 —— 多源结果融合 + 逻辑自洽检查"""

from typing import List, Dict, Any, Tuple


def group_by_dimension(new_info: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """将多个 Skill 的结果按维度分组"""
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for dim, info in new_info.items():
        if dim not in groups:
            groups[dim] = []
        groups[dim].append(info)
    return groups


def all_same(values: List[Any]) -> bool:
    """检查列表中所有值是否相同"""
    if not values:
        return True
    first = values[0]
    # 列表类型的相等比较
    if isinstance(first, list):
        return all(sorted(v) == sorted(first) if isinstance(v, list) else False for v in values[1:])
    if isinstance(first, dict):
        return all(v == first for v in values[1:])
    return all(v == first for v in values[1:])


def majority_vote(values: List[Any]) -> Any:
    """多数投票"""
    from collections import Counter
    # 列表类型转成 tuple 再投票
    if values and isinstance(values[0], list):
        hashable = [tuple(sorted(v)) if isinstance(v, list) else v for v in values]
        counter = Counter(hashable)
        winner = counter.most_common(1)[0][0]
        return list(winner) if isinstance(winner, tuple) else winner
    counter = Counter(values)
    return counter.most_common(1)[0][0]


def merge_and_validate(new_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    多源交叉验证：
    - 多源一致 → 加权提升置信度
    - 来源冲突 → 多数投票，降置信度
    """
    groups = group_by_dimension(new_info)
    merged = {}

    for dim, predictions in groups.items():
        if len(predictions) == 1:
            merged[dim] = {
                "value": predictions[0].get("value"),
                "confidence": predictions[0].get("confidence", 0.0),
                "sources": [predictions[0].get("source", "unknown")],
                "verified": False,
            }
            continue

        values = [p.get("value") for p in predictions]
        confidences = [p.get("confidence", 0.0) for p in predictions]
        sources = [p.get("source", "unknown") for p in predictions]

        if all_same(values):
            merged[dim] = {
                "value": values[0],
                "confidence": min(1.0, max(confidences) * 1.2),
                "sources": sources,
                "verified": True,
            }
        else:
            consensus = majority_vote(values)
            agreement_ratio = sum(1 for v in values if v == consensus) / len(values)
            merged[dim] = {
                "value": consensus,
                "confidence": max(confidences) * agreement_ratio * 0.8,
                "sources": sources,
                "verified": False,
                "conflict_detail": f"来源 {sources} 分别预测 {values}",
            }

    return merged


# ═══════════════════════════════════════════════════════
# 逻辑自洽检查
# ═══════════════════════════════════════════════════════

CONSISTENCY_RULES = [
    # (规则描述, 检查函数)
    (
        "大型项目预算不应过低",
        lambda r: not (
            _get_val(r, "complexity") == "high"
            and _get_budget_max(r) is not None
            and _get_budget_max(r) < 100000
        ),
    ),
    (
        "AI项目工期不应过短",
        lambda r: not (
            "AI" in str(_get_val(r, "primary_need", ""))
            and _get_val(r, "timeline") in ("1个月", "2-4周")
        ),
    ),
    (
        "电商平台技能应包含后端",
        lambda r: not (
            "电商" in str(_get_val(r, "domain", ""))
            and _get_val(r, "required_skills")
            and not any(
                s in str(_get_val(r, "required_skills")).lower()
                for s in ["java", "python", "node", "后端", "数据库", "spring"]
            )
        ),
    ),
]


def _get_val(req: Dict[str, Any], key: str, default: Any = None) -> Any:
    """从需求画像中获取值（可能是直接值或嵌套的 value）"""
    item = req.get(key, default)
    if isinstance(item, dict):
        return item.get("value", default)
    return item


def _get_budget_max(req: Dict[str, Any]) -> Any:
    budget = req.get("estimated_budget_range", {})
    if isinstance(budget, dict):
        val = budget.get("value", {})
        if isinstance(val, dict):
            return val.get("max")
    return None


def check_logical_consistency(requirement: Dict[str, Any]) -> List[str]:
    """
    检查需求画像的逻辑自洽性。

    返回违规描述的列表（空列表 = 全部自洽）
    """
    violations = []
    for desc, check_fn in CONSISTENCY_RULES:
        try:
            if not check_fn(requirement):
                violations.append(desc)
        except Exception:
            pass
    return violations
