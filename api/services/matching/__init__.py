"""匹配系统 —— 关键词匹配（稳定版）

使用方式：
    from services.matching import match_opc_profiles

    matches = match_opc_profiles(demand, opc_profiles)
"""

from __future__ import annotations
from typing import List, Dict, Any
import logging
import re

from models.schemas import DemandProfileOut, OPCMatch

logger = logging.getLogger("uvicorn")


def match_opc_profiles(
    demand: DemandProfileOut,
    opc_profiles: List[Dict[str, Any]],
    top_k: int = 8,
    min_score: float = 0.0,
) -> List[OPCMatch]:
    """简化的关键词匹配（稳定版）"""
    if not opc_profiles:
        return []

    search_parts = []
    if demand.project_type:
        search_parts.append(demand.project_type)
    if demand.description:
        search_parts.append(demand.description)
    if demand.industry:
        search_parts.append(demand.industry)
    if demand.skills_required:
        search_parts.append(" ".join(demand.skills_required))
    search_text = " ".join(search_parts)

    if not search_text.strip():
        results = [(p, 50.0) for p in opc_profiles]
    else:
        results = []
        for p in opc_profiles:
            opc_text = " ".join([
                p.get("role") or "",
                p.get("description") or "",
                p.get("skills") or "",
            ])
            score = _keyword_match_score(search_text, opc_text)
            if p.get("is_available", True):
                score = min(100.0, score + 5.0)
            results.append((p, round(score, 1)))

    results.sort(key=lambda x: x[1], reverse=True)
    filtered = [(p, s) for p, s in results if s >= min_score][:top_k]

    matches: List[OPCMatch] = []
    for profile, score in filtered:
        skills = _parse_skills(profile.get("skills") or "")
        role = profile.get("role") or ""
        name = profile.get("name") or ""
        reasons = []
        if score >= 60:
            reasons.append(f"擅长{role}，和你的需求匹配度较高")
        else:
            reasons.append(f"具备{role}能力，可以满足基本需求")

        matches.append(OPCMatch(
            id=profile.get("id", ""),
            name=name,
            avatar_url=profile.get("avatar_url"),
            role=role,
            description=profile.get("description"),
            skills=skills,
            match_rate=score,
            match_reasons=reasons,
            is_available=profile.get("is_available", True),
        ))
    return matches


def _keyword_match_score(search_text: str, opc_text: str) -> float:
    """改进的中文关键词匹配"""
    search_words = re.split(r'[,，、\s]+', search_text)
    search_words = [w.strip() for w in search_words if len(w.strip()) >= 1]
    if not search_words:
        return 30.0

    search_no_space = search_text.replace(" ", "")
    opc_no_space = opc_text.replace(" ", "")
    total = len(search_words)
    hits = 0.0
    for word in search_words:
        if word in opc_text:
            hits += 1.0
            continue
        word_no_space = word.replace(" ", "")
        if len(word_no_space) >= 2 and word_no_space in opc_no_space:
            hits += 0.8
            continue
        if len(word_no_space) >= 2:
            matched = False
            if len(word_no_space) >= 3:
                for i in range(len(word_no_space) - 2):
                    chunk = word_no_space[i:i + 3]
                    if chunk in opc_no_space:
                        hits += 0.6
                        matched = True
                        break
            if not matched:
                for i in range(len(word_no_space) - 1):
                    chunk = word_no_space[i:i + 2]
                    if chunk in opc_no_space:
                        hits += 0.4
                        break

    score = (hits / total) * 100.0
    return max(15.0, min(100.0, score))


def _parse_skills(skills_str: str) -> List[str]:
    """解析逗号分隔的技能字符串"""
    if not skills_str:
        return []
    return [s.strip() for s in skills_str.split(",") if s.strip()]
