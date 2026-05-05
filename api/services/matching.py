"""OPC 匹配引擎 —— 多维度精准匹配"""

from typing import List, Dict, Any
from models.schemas import DemandProfileOut, OPCMatch
from services.embedding import embed_texts, cosine_similarity, clear_cache
from services.llm import chat_completion
from services import prompting, extraction


def match_opc_profiles(
    demand: DemandProfileOut,
    opc_profiles: List[Dict[str, Any]],
    top_k: int = 8,
    min_score: float = 40.0,
) -> List[OPCMatch]:
    """
    多维度匹配 OPC 画像，返回排序后的 Top-K 匹配结果。

    匹配维度与权重（「找人」导向）：
    1. 技能语义匹配    (30%) — 嵌入向量余弦相似度
    2. 角色适配度      (35%) — LLM 评估角色匹配，找对人的核心
    3. 描述相关性      (20%) — 嵌入向量余弦相似度
    4. 行业经验        (10%) — 需求行业与 OPC 描述的语义匹配
    5. 可接单状态       (5%) — 在线加分

    返回带评分理由的匹配列表。
    """
    if not opc_profiles:
        return []

    # 清理缓存
    clear_cache()

    # ── 维度 1: 技能语义匹配 ──────────────────────
    skill_scores = _compute_skill_scores(demand, opc_profiles)

    # ── 维度 2: 角色适配度 ────────────────────────
    role_scores = _compute_role_scores(demand, opc_profiles)

    # ── 维度 3: 描述相关性 ────────────────────────
    desc_scores = _compute_description_scores(demand, opc_profiles)

    # ── 维度 4: 行业经验 ──────────────────────────
    industry_scores = _compute_industry_scores(demand, opc_profiles)

    # ── 维度 5: 可接单状态 ────────────────────────
    availability_scores = [
        100.0 if p.get("is_available", True) else 30.0 for p in opc_profiles
    ]

    # ── 加权融合 ──────────────────────────────────
    results: List[tuple] = []
    for i, profile in enumerate(opc_profiles):
        weighted = (
            skill_scores[i] * 0.30
            + role_scores[i] * 0.35
            + desc_scores[i] * 0.20
            + industry_scores[i] * 0.10
            + availability_scores[i] * 0.05
        )
        results.append((profile, round(weighted, 1)))

    # 排序 + 过滤
    results.sort(key=lambda x: x[1], reverse=True)
    filtered = [(p, s) for p, s in results if s >= min_score][:top_k]

    # ── 生成匹配解释 ──────────────────────────────
    matches: List[OPCMatch] = []
    for profile, score in filtered:
        skills = _parse_skills(profile.get("skills", ""))
        reasons = _generate_match_reasons(
            demand, profile.get("name", ""), profile.get("role", ""),
            skills, profile.get("description", ""), score,
            skill_scores[opc_profiles.index(profile)],
            role_scores[opc_profiles.index(profile)],
        )
        matches.append(OPCMatch(
            id=profile.get("id", ""),
            name=profile.get("name", ""),
            avatar_url=profile.get("avatar_url"),
            role=profile.get("role", ""),
            description=profile.get("description"),
            skills=skills,
            match_rate=score,
            match_reasons=reasons,
            is_available=profile.get("is_available", True),
        ))

    return matches


def _compute_skill_scores(
    demand: DemandProfileOut,
    opc_profiles: List[Dict[str, Any]],
) -> List[float]:
    """计算技能语义匹配分数 [0, 100]"""
    req_skills = "、".join(demand.skills_required) if demand.skills_required else demand.description
    if not req_skills.strip():
        return [50.0] * len(opc_profiles)  # 无技能需求时默认中等分

    texts = [req_skills] + [
        p.get("skills", "") or "" for p in opc_profiles
    ]
    embeddings = embed_texts(texts)
    req_emb = embeddings[0]
    opc_embs = embeddings[1:]

    return [cosine_similarity(req_emb, emb) * 100.0 for emb in opc_embs]


def _compute_role_scores(
    demand: DemandProfileOut,
    opc_profiles: List[Dict[str, Any]],
) -> List[float]:
    """通过 LLM 评估角色适配度 [0, 100]（串行调用，保证 Vercel serverless 兼容性）"""
    if not demand.project_type:
        return [50.0] * len(opc_profiles)

    def _score_one(index: int, profile: Dict[str, Any]) -> tuple[int, float]:
        try:
            resp = chat_completion(
                messages=[
                    {"role": "system", "content": prompting.ROLE_MATCH_SYSTEM},
                    {"role": "user", "content": prompting.build_role_match_prompt(
                        project_type=demand.project_type,
                        project_desc=demand.description,
                        opc_role=profile.get("role", ""),
                        opc_desc=profile.get("description", ""),
                        project_scope=demand.project_scope,
                        target_users=demand.target_users,
                        constraints=demand.constraints,
                    )},
                ],
                temperature=0.0,
                max_tokens=4,
                timeout=5.0,
            )
            score = float(resp.strip())
            return index, min(max(score, 0), 100)
        except Exception:
            return index, 50.0

    scores: List[float] = [50.0] * len(opc_profiles)
    for i, profile in enumerate(opc_profiles):
        index, score = _score_one(i, profile)
        scores[index] = score

    return scores


def _compute_description_scores(
    demand: DemandProfileOut,
    opc_profiles: List[Dict[str, Any]],
) -> List[float]:
    """计算需求描述与 OPC 描述的语义相似度 [0, 100]"""
    if not demand.description:
        return [50.0] * len(opc_profiles)

    texts = [demand.description] + [
        p.get("description", "") or "" for p in opc_profiles
    ]
    embeddings = embed_texts(texts)
    req_emb = embeddings[0]
    opc_embs = embeddings[1:]

    return [cosine_similarity(req_emb, emb) * 100.0 for emb in opc_embs]


def _compute_industry_scores(
    demand: DemandProfileOut,
    opc_profiles: List[Dict[str, Any]],
) -> List[float]:
    """计算行业经验匹配度 [0, 100]。未指定行业时默认中等分。"""
    if not demand.industry:
        return [50.0] * len(opc_profiles)

    # 用行业关键词与 OPC 的完整描述做语义匹配
    texts = [demand.industry] + [
        f"{p.get('role', '')} {p.get('description', '')} {p.get('skills', '')}"
        for p in opc_profiles
    ]
    embeddings = embed_texts(texts)
    ind_emb = embeddings[0]
    opc_embs = embeddings[1:]

    return [cosine_similarity(ind_emb, emb) * 100.0 for emb in opc_embs]


def _parse_skills(skills_str: str) -> List[str]:
    """解析逗号分隔的技能字符串"""
    if not skills_str:
        return []
    return [s.strip() for s in skills_str.split(",") if s.strip()]


def _generate_match_reasons(
    demand: DemandProfileOut,
    name: str,
    role: str,
    skills: List[str],
    description: str,
    total_score: float,
    skill_score: float,
    role_score: float,
) -> List[str]:
    """生成匹配理由列表"""
    reasons = []

    # 基于分项得分生成理由
    if skill_score >= 70:
        matched_skills = [s for s in skills if any(
            rs.lower() in s.lower() or s.lower() in rs.lower()
            for rs in demand.skills_required
        )] if demand.skills_required else skills[:2]
        if matched_skills:
            reasons.append(f"技能高度匹配：{', '.join(matched_skills[:3])}")

    if role_score >= 70:
        reasons.append(f"角色高度匹配：{role} 与项目需求契合")

    if total_score >= 80:
        reasons.append("综合匹配度优秀，推荐优先联系")

    # 不重复调用 LLM 为每个 OPC 生成解释（避免延迟和成本），使用规则生成
    if not reasons:
        reasons.append(f"部分技能与需求相关")

    return reasons
