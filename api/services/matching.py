"""OPC 匹配引擎 —— 简化的关键词匹配"""

from typing import List, Dict, Any
from models.schemas import DemandProfileOut, OPCMatch


def match_opc_profiles(
    demand: DemandProfileOut,
    opc_profiles: List[Dict[str, Any]],
    top_k: int = 8,
    min_score: float = 0.0,
) -> List[OPCMatch]:
    """
    简化的关键词匹配，不做 embedding 和 LLM 评分。

    匹配逻辑：
    1. 从用户需求中提取关键信息（项目类型 + 描述 + 行业 + 技能需求）
    2. 与每个 OPC 的角色、描述、技能做文本重合度计算
    3. 排序返回结果
    """
    if not opc_profiles:
        return []

    # 构建搜索文本（包含 skills_required 以提高匹配精度）
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
        # 没有任何需求信息时，全部返回基础分
        results = [(p, 50.0) for p in opc_profiles]
    else:
        results = []
        for p in opc_profiles:
            opc_text = " ".join([
                p.get("role", ""),
                p.get("description", ""),
                p.get("skills", ""),
            ])
            score = _keyword_match_score(search_text, opc_text)
            if p.get("is_available", True):
                score = min(100.0, score + 5.0)
            results.append((p, round(score, 1)))

    results.sort(key=lambda x: x[1], reverse=True)
    filtered = [(p, s) for p, s in results if s >= min_score][:top_k]

    matches: List[OPCMatch] = []
    for profile, score in filtered:
        skills = _parse_skills(profile.get("skills", ""))
        role = profile.get("role", "")
        name = profile.get("name", "")

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
    """
    改进的中文关键词匹配。

    策略：
    1. 提取搜索文本中的词片段（按标点和空格分词）
    2. 先去空格做精确匹配（解决"AI客服" vs "AI 客服系统架构师"的问题）
    3. 再去空格做 2-3 字子串匹配
    4. 归一化到 0-100
    """
    import re

    # 按标点和空格分词
    search_words = re.split(r'[,，、\s]+', search_text)
    search_words = [w.strip() for w in search_words if len(w.strip()) >= 1]

    if not search_words:
        return 30.0

    # 去空格版本，用于解决中文词中间的空格问题
    search_no_space = search_text.replace(" ", "")
    opc_no_space = opc_text.replace(" ", "")

    total = len(search_words)
    hits = 0.0
    for word in search_words:
        # 策略1：原文精确匹配
        if word in opc_text:
            hits += 1.0
            continue

        # 策略2：去空格后精确匹配（如 "AI客服" 能匹配 "AI 客服系统架构师"）
        word_no_space = word.replace(" ", "")
        if len(word_no_space) >= 2 and word_no_space in opc_no_space:
            hits += 0.8
            continue

        # 策略3：去空格后 2-3 字子串匹配
        if len(word_no_space) >= 2:
            matched = False
            # 先尝试 3 字子串
            if len(word_no_space) >= 3:
                for i in range(len(word_no_space) - 2):
                    chunk = word_no_space[i:i+3]
                    if chunk in opc_no_space:
                        hits += 0.6
                        matched = True
                        break
            # 再尝试 2 字子串
            if not matched:
                for i in range(len(word_no_space) - 1):
                    chunk = word_no_space[i:i+2]
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
