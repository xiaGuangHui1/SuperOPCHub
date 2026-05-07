"""关联规则 —— 从历史数据预挖掘的统计模式"""

from typing import List, Dict, Any, Optional


# ═══════════════════════════════════════════════════════
# 预定义关联规则（初期手工配置，后期可离线挖掘替代）
# ═══════════════════════════════════════════════════════

# 格式: antecedent -> consequent, confidence, lift
# antecedent: 已知条件 {"field": "value"}
# consequent: 推断结果 {"field": "value"}
ASSOCIATION_RULES = [
    # 项目类型 → 领域
    {"antecedent": {"project_type": "AI客服"}, "consequent": {"domain": "AI/智能"}, "confidence": 0.85, "lift": 3.2},
    {"antecedent": {"project_type": "电商平台"}, "consequent": {"domain": "电商"}, "confidence": 0.90, "lift": 3.8},
    {"antecedent": {"project_type": "小程序"}, "consequent": {"domain": "电商"}, "confidence": 0.78, "lift": 2.5},
    {"antecedent": {"project_type": "网站建设"}, "consequent": {"domain": "企业服务"}, "confidence": 0.72, "lift": 2.1},

    # 领域 → 技能
    {"antecedent": {"domain": "AI/智能"}, "consequent": {"skills": ["Python", "NLP", "机器学习"]}, "confidence": 0.82, "lift": 2.8},
    {"antecedent": {"domain": "电商"}, "consequent": {"skills": ["Java", "支付集成", "Vue.js"]}, "confidence": 0.76, "lift": 2.3},
    {"antecedent": {"domain": "企业服务"}, "consequent": {"skills": ["Java", "Vue.js", "数据库设计"]}, "confidence": 0.70, "lift": 1.9},
    {"antecedent": {"domain": "内容/媒体"}, "consequent": {"skills": ["视频处理", "流媒体", "CMS"]}, "confidence": 0.68, "lift": 2.4},

    # 项目类型 → 预算
    {"antecedent": {"project_type": "AI客服"}, "consequent": {"budget": {"min": 100000, "max": 300000}}, "confidence": 0.65, "lift": 2.1},
    {"antecedent": {"project_type": "电商平台"}, "consequent": {"budget": {"min": 150000, "max": 500000}}, "confidence": 0.70, "lift": 2.5},
    {"antecedent": {"project_type": "小程序"}, "consequent": {"budget": {"min": 50000, "max": 200000}}, "confidence": 0.72, "lift": 2.6},

    # 项目类型 → 工期
    {"antecedent": {"project_type": "AI客服"}, "consequent": {"timeline": "2-3个月"}, "confidence": 0.68, "lift": 1.8},
    {"antecedent": {"project_type": "网站建设"}, "consequent": {"timeline": "1个月"}, "confidence": 0.75, "lift": 2.0},
    {"antecedent": {"project_type": "小程序"}, "consequent": {"timeline": "1-2月"}, "confidence": 0.80, "lift": 2.2},
    {"antecedent": {"project_type": "电商平台"}, "consequent": {"timeline": "3-6个月"}, "confidence": 0.65, "lift": 1.5},
]

# 贝叶斯先验（基于常见需求分布）
BAYESIAN_PRIORS = {
    "domain": {
        "企业服务": 0.30,
        "电商": 0.20,
        "AI/智能": 0.15,
        "内容/媒体": 0.10,
        "教育": 0.08,
        "金融": 0.07,
        "医疗": 0.05,
        "其他": 0.05,
    },
    "complexity": {
        "low": 0.40,
        "medium": 0.40,
        "high": 0.20,
    },
    "timeline": {
        "1个月": 0.25,
        "1-2月": 0.30,
        "2-3个月": 0.25,
        "3-6个月": 0.15,
        "6个月以上": 0.05,
    },
}


def load_association_rules() -> List[Dict[str, Any]]:
    """加载关联规则（后续可从 DB 加载）"""
    return ASSOCIATION_RULES


def match_rules(known_slots: Dict[str, str]) -> List[Dict[str, Any]]:
    """根据已知字段匹配关联规则"""
    rules = load_association_rules()
    matched = []

    for rule in rules:
        antecedent = rule["antecedent"]
        if all(known_slots.get(k) == v for k, v in antecedent.items()):
            matched.append(rule)

    return matched


def bayesian_predict(
    slot: str,
    known_slots: Dict[str, str],
    historical_count: int = 100,
) -> Dict[str, Any]:
    """
    贝叶斯推断未知维度。
    简化版：使用先验分布 + 少量条件概率更新。
    """
    priors = BAYESIAN_PRIORS.get(slot, {})
    if not priors:
        return {"value": "", "confidence": 0.0, "source": "bayesian"}

    # 简单 Naive Bayes：使用关联规则的条件概率更新先验
    rules = load_association_rules()
    relevant_rules = [
        r for r in rules
        if r["consequent"].get(slot)
        and all(known_slots.get(k) == v for k, v in r["antecedent"].items())
    ]

    if not relevant_rules:
        # 无关联规则命中，返回先验最大值
        best = max(priors, key=priors.get)
        return {
            "value": best,
            "confidence": min(0.5, priors[best]),
            "source": "bayesian_prior",
        }

    # 取置信度最高的规则结果
    best_rule = max(relevant_rules, key=lambda r: r["confidence"] * r["lift"])
    value = best_rule["consequent"].get(slot)

    return {
        "value": value if isinstance(value, str) else str(value),
        "confidence": min(0.8, best_rule["confidence"]),
        "source": "bayesian_inference",
        "lift": best_rule["lift"],
    }
