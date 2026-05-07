"""反馈闭环 —— 采集用户行为信号并调整匹配权重"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("uvicorn")

# 全局反馈累积（生产环境应改用 DB/Redis）
_feedback_store: List[Dict[str, Any]] = []


def record_feedback(
    user_id: str,
    session_id: str,
    signal_type: str,
    data: Dict[str, Any],
) -> None:
    """
    记录用户反馈信号。

    signal_type:
    - "confirm_no_change": 用户确认未修改
    - "correct_field": 用户修正了某字段
    - "view_opc": 用户查看了 OPC 详情
    - "contact_opc": 用户发起了联系
    - "ignore_recommendation": 用户忽略了推荐
    """
    feedback = {
        "user_id": user_id,
        "session_id": session_id,
        "type": signal_type,
        "data": data,
    }
    _feedback_store.append(feedback)
    logger.info(f"[Feedback] 记录信号: {signal_type} session={session_id}")


def get_correction_signals(session_id: str) -> List[Dict[str, Any]]:
    """获取某会话的用户修正记录"""
    return [
        f for f in _feedback_store
        if f["session_id"] == session_id and f["type"] == "correct_field"
    ]


def get_positive_signals(user_id: str) -> List[Dict[str, Any]]:
    """获取用户正反馈信号"""
    return [
        f for f in _feedback_store
        if f["user_id"] == user_id
        and f["type"] in ("confirm_no_change", "contact_opc", "view_opc")
    ]


def get_negative_signals(user_id: str) -> List[Dict[str, Any]]:
    """获取用户负反馈信号"""
    return [
        f for f in _feedback_store
        if f["user_id"] == user_id
        and f["type"] in ("correct_field", "ignore_recommendation")
    ]


def adjust_skill_weights(session_id: str) -> Dict[str, float]:
    """
    基于反馈调整 Skill 权重。

    逻辑：
    - 用户确认未修改 → 提示 RAG 和 KG 权重有效，小幅提升
    - 用户修正字段 → 降低当前字段主要来源的 Skill 权重
    """
    corrections = get_correction_signals(session_id)

    # 初始权重
    weights = {
        "RAG_historical": 1.0,
        "knowledge_graph": 1.0,
        "statistical_match": 1.0,
        "LLM_reasoning": 1.0,
    }

    for corr in corrections:
        field = corr["data"].get("field", "")
        # 如果用户修正了某字段，降低最常见来源的权重
        if field in ("domain", "project_type", "primary_need"):
            weights["RAG_historical"] *= 0.95
        elif field in ("required_skills",):
            weights["knowledge_graph"] *= 0.95
        elif field in ("budget", "timeline"):
            weights["statistical_match"] *= 0.95

    return weights
