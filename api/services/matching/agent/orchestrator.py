"""需求分析 Agent 主控循环 —— 多轮推理 + 交叉验证"""

from typing import List, Dict, Any, Optional
import logging

from services.matching.agent.skills.rag_completion import skill_rag_completion
from services.matching.agent.skills.kg_reasoning import skill_kg_reasoning
from services.matching.agent.skills.statistical import skill_statistical_inference
from services.matching.agent.skills.llm_reasoning import skill_llm_reasoning
from services.matching.agent.validation import merge_and_validate, check_logical_consistency
from services.matching.agent.critique import self_critique, apply_critique_adjustments
from services.matching.schemas import (
    EnhancedDemandProfile,
    InferenceDimension,
    SkillDimensions,
    BudgetDimension,
)

logger = logging.getLogger("uvicorn")

DIMENSION_LIST = [
    "primary_need", "domain", "required_skills", "complexity",
    "estimated_budget_range", "timeline", "industry", "constraints", "description"
]


class RequirementAnalysisAgent:
    """
    需求分析 Agent。

    核心流程：
    Round 0: 初始解析 → 提取已有信息，标记缺失
    Round 1: 广撒网 → RAG + KG + Stats 并行
    Round 2: 深挖 → LLM 推理 + 交叉验证
    Round 3: 兜底 → LLM Self-Critique
    """

    def __init__(
        self,
        max_rounds: int = 3,
        confidence_threshold: float = 0.7,
    ):
        self.max_rounds = max_rounds
        self.threshold = confidence_threshold
        self.pool: Dict[str, Any] = {}
        self.confidence_history: List[float] = []

    def analyze(
        self,
        user_input: str,
        behavioral_signals: Optional[Dict[str, Any]] = None,
        initial_extraction: Optional[Dict[str, Any]] = None,
    ) -> EnhancedDemandProfile:
        """
        执行需求分析。

        :param user_input: 用户原始输入文本
        :param behavioral_signals: 用户行为信号
        :param initial_extraction: 已有的 LLM 初步提取结果（复用现有 extraction 模块）
        :return: 增强版需求画像
        """
        # Round 0: 初始解析
        self._initial_parse(user_input, initial_extraction)
        logger.info(f"[Agent] Round 0 完成, pool keys: {list(self.pool.keys())}")

        for round_num in range(1, self.max_rounds + 1):
            gaps = self.identify_gaps(self.threshold)
            logger.info(f"[Agent] Round {round_num}, gaps: {gaps}")

            if not gaps:
                logger.info("[Agent] 全部维度达标，提前退出")
                break

            strategy = self._plan_strategy(gaps, round_num)
            new_info = self._execute_skills_parallel(strategy, user_input, behavioral_signals)
            merged = merge_and_validate(new_info)
            self._update_pool(merged)

            # 记录当前平均置信度
            self.confidence_history.append(self._avg_confidence())

            stop_reason = self._should_stop(round_num, gaps)
            if stop_reason:
                logger.info(f"[Agent] 退出循环: {stop_reason}")
                break

        # 最终轮: Self-Critique
        critique_result = self.critique(user_input)
        if critique_result:
            self.pool = apply_critique_adjustments(self.pool, critique_result)

        # 逻辑自洽检查
        violations = check_logical_consistency(self.pool)
        if violations:
            logger.warning(f"[Agent] 逻辑自洽违规: {violations}")
            # 降低整体置信度
            for dim in self.pool:
                if isinstance(self.pool[dim], dict) and "confidence" in self.pool[dim]:
                    self.pool[dim]["confidence"] *= 0.9

        return self._build_output()

    # ── Round 0: 初始解析 ──────────────────────────────

    def _initial_parse(
        self,
        user_input: str,
        initial_extraction: Optional[Dict[str, Any]] = None,
    ):
        """从用户输入和已有的 LLM 提取结果中解析已知信息"""
        self.pool = {}

        if initial_extraction:
            # 映射已有提取结果
            mapping = {
                "primary_need": "project_type",
                "domain": "industry",
                "description": "description",
                "timeline": "timeline",
                "industry": "industry",
            }
            for dim, field in mapping.items():
                val = initial_extraction.get(field, "")
                if val:
                    self.pool[dim] = {
                        "value": val,
                        "confidence": 0.9 if field == "project_type" else 0.7,
                        "sources": ["LLM_extraction"],
                        "verified": False,
                    }

            # 技能
            skills = initial_extraction.get("skills_required", [])
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(",") if s.strip()]
            if skills:
                self.pool["required_skills"] = {
                    "value": skills,
                    "confidence": 0.7,
                    "sources": ["LLM_extraction"],
                    "verified": False,
                    "mandatory": skills[:3],
                    "optional": skills[3:],
                }

            # 预算
            bmin = initial_extraction.get("budget_min")
            bmax = initial_extraction.get("budget_max")
            if bmin or bmax:
                self.pool["estimated_budget_range"] = {
                    "value": {"min": bmin, "max": bmax},
                    "confidence": 0.6,
                    "sources": ["LLM_extraction"],
                    "verified": False,
                }

            # 复杂度：从 project_scope 推断
            scope = initial_extraction.get("project_scope", "")
            if scope:
                self.pool["complexity"] = {
                    "value": "medium",
                    "confidence": 0.5,
                    "sources": ["LLM_extraction"],
                    "verified": False,
                }

    # ── Gap 识别 ──────────────────────────────────────

    def identify_gaps(self, threshold: float) -> List[str]:
        """找出置信度低于阈值的维度"""
        gaps = []
        for dim in DIMENSION_LIST:
            if dim not in self.pool:
                gaps.append(dim)
            elif isinstance(self.pool[dim], dict):
                conf = self.pool[dim].get("confidence", 0.0)
                if conf < threshold:
                    gaps.append(dim)
        return gaps

    # ── 策略规划 ──────────────────────────────────────

    def _plan_strategy(self, gaps: List[str], round_num: int) -> List[str]:
        """根据轮次规划执行的 Skill"""
        if round_num == 1:
            return ["RAG_historical", "knowledge_graph", "statistical_match"]
        elif round_num == 2:
            return ["RAG_historical", "LLM_deep_reasoning"]
        else:
            return ["LLM_final_fill"]

    # ── Skill 执行 ────────────────────────────────────

    def _execute_skills_parallel(
        self,
        strategy: List[str],
        user_input: str,
        behavioral_signals: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """执行指定策略的 Skill（顺序执行，同策略内可并行）"""
        all_results = {}

        for skill_name in strategy:
            try:
                if skill_name == "RAG_historical":
                    gaps = self.identify_gaps(self.threshold)
                    results = skill_rag_completion(user_input, gaps)
                    all_results.update(results)

                elif skill_name == "knowledge_graph":
                    known = self._get_known_simple()
                    known["project_type"] = self._get_pool_val("primary_need") or ""
                    gaps = self.identify_gaps(self.threshold)
                    results = skill_kg_reasoning(user_input, known, gaps)
                    all_results.update(results)

                elif skill_name == "statistical_match":
                    results = skill_statistical_inference(self._get_known_simple())
                    all_results.update(results)

                elif skill_name == "LLM_deep_reasoning" or skill_name == "LLM_final_fill":
                    gaps = self.identify_gaps(self.threshold - 0.15)
                    collected = {k: v for k, v in self.pool.items()}
                    results = skill_llm_reasoning(
                        user_input, collected, gaps, behavioral_signals
                    )
                    all_results.update(results)

            except Exception as e:
                logger.error(f"[Agent] Skill {skill_name} 执行失败: {e}")

        return all_results

    # ── 退出判定 ──────────────────────────────────────

    def _should_stop(self, round_num: int, gaps: List[str]) -> Optional[str]:
        if not gaps:
            return "all_confident"
        if round_num >= self.max_rounds:
            return "max_rounds"
        if len(self.confidence_history) >= 2:
            improvement = self.confidence_history[-1] - self.confidence_history[-2]
            if improvement < 0.05:
                return "no_improvement"
        return None

    # ── 辅助方法 ──────────────────────────────────────

    def _update_pool(self, merged: Dict[str, Any]):
        """更新需求池（合并新信息）"""
        for dim, info in merged.items():
            if dim in self.pool and isinstance(self.pool[dim], dict):
                # 已有该维度：取更高置信度的来源
                old_conf = self.pool[dim].get("confidence", 0.0)
                new_conf = info.get("confidence", 0.0)
                if new_conf > old_conf:
                    self.pool[dim] = info
            else:
                self.pool[dim] = info

    def _get_pool_val(self, dim: str) -> Any:
        info = self.pool.get(dim)
        if isinstance(info, dict):
            return info.get("value")
        return info

    def _get_known_simple(self) -> Dict[str, Any]:
        """获取已知字段的简单值映射"""
        simple = {}
        for dim in DIMENSION_LIST:
            val = self._get_pool_val(dim)
            if val:
                simple[dim] = val
        return simple

    def _avg_confidence(self) -> float:
        confs = []
        for dim in DIMENSION_LIST:
            info = self.pool.get(dim)
            if isinstance(info, dict):
                confs.append(info.get("confidence", 0.0))
        return sum(confs) / len(confs) if confs else 0.0

    def critique(self, user_input: str) -> Optional[Dict[str, Any]]:
        """执行 Self-Critique"""
        if not self.pool:
            return None
        try:
            return self_critique(user_input, self.pool)
        except Exception as e:
            logger.error(f"[Agent] Self-Critique 失败: {e}")
            return None

    # ── 输出构建 ──────────────────────────────────────

    def _build_output(self) -> EnhancedDemandProfile:
        """构建增强版需求画像输出"""
        def make_dim(dim_name: str) -> InferenceDimension:
            info = self.pool.get(dim_name, {})
            if not isinstance(info, dict):
                return InferenceDimension(value=info or "", confidence=0.0)
            return InferenceDimension(
                value=info.get("value", ""),
                confidence=info.get("confidence", 0.0),
                sources=info.get("sources", []),
                verified=info.get("verified", False),
                alternatives=info.get("alternatives", []),
            )

        def make_skill_dim() -> SkillDimensions:
            info = self.pool.get("required_skills", {})
            if not isinstance(info, dict):
                return SkillDimensions(value=info if isinstance(info, list) else [])
            return SkillDimensions(
                value=info.get("value", []),
                confidence=info.get("confidence", 0.0),
                sources=info.get("sources", []),
                verified=info.get("verified", False),
                mandatory=info.get("mandatory", []),
                optional=info.get("optional", []),
            )

        def make_budget_dim() -> BudgetDimension:
            info = self.pool.get("estimated_budget_range", {})
            if not isinstance(info, dict):
                return BudgetDimension()
            return BudgetDimension(
                value=info.get("value", {"min": None, "max": None}),
                confidence=info.get("confidence", 0.0),
                sources=info.get("sources", []),
                verified=info.get("verified", False),
            )

        low_conf_dims = [d for d in DIMENSION_LIST
                         if isinstance(self.pool.get(d), dict)
                         and self.pool[d].get("confidence", 0.0) < 0.5]

        return EnhancedDemandProfile(
            raw_input="",
            primary_need=make_dim("primary_need"),
            domain=make_dim("domain"),
            required_skills=make_skill_dim(),
            complexity=make_dim("complexity"),
            estimated_budget_range=make_budget_dim(),
            timeline=make_dim("timeline"),
            industry=make_dim("industry"),
            constraints=make_dim("constraints"),
            description=make_dim("description"),
            total_rounds=self.max_rounds,
            exit_reason=self._should_stop(self.max_rounds, []) or "complete",
            overall_confidence=self._avg_confidence(),
            dimensions_with_low_confidence=low_conf_dims,
            inference_cost={},
        )
