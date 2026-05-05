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
    1. 从用户需求中提取关键信息（项目类型 + 描述 + 行业）
    2. 与每个 OPC 的角色、描述、技能做文本重合度计算
    3. 排序返回结果
    """
    if not opc_profiles:
        return []

    # 构建搜索文本
    search_parts = []
    if demand.project_type:
        search_parts.append(demand.project_type)
    if demand.description:
        search_parts.append(demand.description)
    if demand.industry:
        search_parts.append(demand.industry)
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
    简单的中文关键词匹配。

    策略：
    - 提取搜索文本中长度>=2的词片段
    - 检查在 OPC 文本中的出现次数
    - 归一化到 0-100
    """
    # 按标点和空格分词
    import re
    search_words = re.split(r'[,，、\s]+', search_text)
    search_words = [w.strip() for w in search_words if len(w.strip()) >= 1]

    if not search_words:
        return 30.0

    total = len(search_words)
    hits = 0
    for word in search_words:
        if word in opc_text:
            hits += 1
        elif len(word) >= 2:
            # 对长词，检查部分匹配
            for i in range(len(word) - 1):
                if word[i:i+2] in opc_text:
                    hits += 0.5
                    break

    score = (hits / total) * 100.0
    return max(15.0, min(100.0, score))


def _parse_skills(skills_str: str) -> List[str]:
    """解析逗号分隔的技能字符串"""
    if not skills_str:
        return []
    return [s.strip() for s in skills_str.split(",") if s.strip()]
