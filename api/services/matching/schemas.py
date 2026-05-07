"""匹配系统内部 Schema —— 增强版画像与推理模型"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════
# 推理维度模型（每字段带置信度 + 来源追溯）
# ═══════════════════════════════════════════════════════

class InferenceDimension(BaseModel):
    """单个推理维度的结果"""
    value: Any
    confidence: float = Field(..., ge=0.0, le=1.0)
    sources: List[str] = Field(default_factory=list)
    verified: bool = False
    alternatives: List[Any] = Field(default_factory=list)


class SkillDimensions(BaseModel):
    """技能维度（支持 mandatory/optional 拆分）"""
    value: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    sources: List[str] = Field(default_factory=list)
    verified: bool = False
    mandatory: List[str] = Field(default_factory=list)
    optional: List[str] = Field(default_factory=list)


class BudgetDimension(BaseModel):
    """预算维度"""
    value: Dict[str, Optional[float]] = Field(default_factory=lambda: {"min": None, "max": None})
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    sources: List[str] = Field(default_factory=list)
    verified: bool = False


# ═══════════════════════════════════════════════════════
# 增强版用户需求画像
# ═══════════════════════════════════════════════════════

class EnhancedDemandProfile(BaseModel):
    """增强版用户需求画像 —— 每维度含置信度+来源"""
    demand_id: str = ""
    raw_input: str = ""

    # 推理维度
    primary_need: InferenceDimension = Field(default_factory=lambda: InferenceDimension(value="", confidence=0.0))
    domain: InferenceDimension = Field(default_factory=lambda: InferenceDimension(value="", confidence=0.0))
    required_skills: SkillDimensions = Field(default_factory=SkillDimensions)
    complexity: InferenceDimension = Field(default_factory=lambda: InferenceDimension(value="medium", confidence=0.5))
    estimated_budget_range: BudgetDimension = Field(default_factory=BudgetDimension)
    timeline: InferenceDimension = Field(default_factory=lambda: InferenceDimension(value="", confidence=0.0))
    industry: InferenceDimension = Field(default_factory=lambda: InferenceDimension(value="", confidence=0.0))
    constraints: InferenceDimension = Field(default_factory=lambda: InferenceDimension(value=[], confidence=0.0))
    description: InferenceDimension = Field(default_factory=lambda: InferenceDimension(value="", confidence=0.0))

    # 推理元信息
    total_rounds: int = 0
    exit_reason: str = ""
    overall_confidence: float = 0.0
    dimensions_with_low_confidence: List[str] = Field(default_factory=list)
    inference_cost: Dict[str, int] = Field(default_factory=dict)

    # 行为信号
    behavioral_signals: Dict[str, Any] = Field(default_factory=dict)

    # 用户修正记录
    user_corrections: Dict[str, Dict[str, str]] = Field(default_factory=dict)

    # 向量
    embedding: List[float] = Field(default_factory=list)

    def get_high_confidence_dimensions(self, threshold: float = 0.6) -> Dict[str, Any]:
        """获取置信度高于阈值的维度简单值"""
        result = {}
        dims = [
            ("primary_need", self.primary_need),
            ("domain", self.domain),
            ("complexity", self.complexity),
            ("timeline", self.timeline),
            ("industry", self.industry),
            ("description", self.description),
        ]
        for name, dim in dims:
            if dim.confidence >= threshold:
                result[name] = dim.value
        if self.required_skills.confidence >= threshold:
            result["required_skills"] = {
                "all": self.required_skills.value,
                "mandatory": self.required_skills.mandatory,
                "optional": self.required_skills.optional,
            }
        if self.estimated_budget_range.confidence >= threshold:
            result["estimated_budget_range"] = self.estimated_budget_range.value
        if self.constraints.confidence >= threshold:
            result["constraints"] = self.constraints.value
        return result


# ═══════════════════════════════════════════════════════
# 增强版 OPC 能力画像
# ═══════════════════════════════════════════════════════

class SkillInfo(BaseModel):
    skill: str
    level: float = Field(default=0.5, ge=0.0, le=1.0)
    years: int = 0


class PortfolioItem(BaseModel):
    title: str = ""
    description: str = ""
    skills_used: List[str] = Field(default_factory=list)
    budget_range: Dict[str, Optional[float]] = Field(default_factory=lambda: {"min": None, "max": None})
    duration_months: int = 0
    embedding: List[float] = Field(default_factory=list)


class EnhancedOPCProfile(BaseModel):
    """增强版 OPC 能力画像"""
    opc_id: str = ""
    name: str = ""
    bio: str = ""

    capabilities: Dict[str, Any] = Field(default_factory=lambda: {
        "primary_skills": [],
        "secondary_skills": [],
        "domains": [],
        "service_types": [],
        "typical_project_scale": "medium",
        "past_project_types": [],
    })

    portfolio: List[Dict[str, Any]] = Field(default_factory=list)

    pricing: Dict[str, Any] = Field(default_factory=lambda: {
        "min_rate": 0, "max_rate": 0, "unit": "hour"
    })

    availability: Dict[str, Any] = Field(default_factory=lambda: {
        "status": "available", "current_load": 0.0, "avg_response_hours": 24
    })

    reputation: Dict[str, Any] = Field(default_factory=lambda: {
        "rating": 3.0, "review_count": 0, "completion_rate": 1.0,
        "review_keywords": []
    })

    embedding: List[float] = Field(default_factory=list)

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "EnhancedOPCProfile":
        """从 Supabase 行数据构建 OPC 画像"""
        skills_str = row.get("skills", "") or ""
        skills_list = [s.strip() for s in skills_str.split(",") if s.strip()]

        return cls(
            opc_id=row.get("id", ""),
            name=row.get("name", ""),
            bio=row.get("description", "") or "",
            capabilities={
                "primary_skills": [{"skill": s, "level": 0.8, "years": 0} for s in skills_list],
                "secondary_skills": [],
                "domains": [row.get("role", "")] if row.get("role") else [],
                "service_types": [],
                "typical_project_scale": "medium",
                "past_project_types": [],
            },
            portfolio=[],
            pricing={"min_rate": 0, "max_rate": 0, "unit": "hour"},
            availability={
                "status": "available" if row.get("is_available", True) else "busy",
                "current_load": 0.0,
                "avg_response_hours": 2,
            },
            reputation={
                "rating": 4.0,
                "review_count": 0,
                "completion_rate": 1.0,
                "review_keywords": [],
            },
        )


# ═══════════════════════════════════════════════════════
# 匹配结果
# ═══════════════════════════════════════════════════════

class MatchDetail(BaseModel):
    """匹配分项得分"""
    semantic_similarity: float = 0.0
    skill_match: float = 0.0
    experience_match: float = 0.0
    reputation_score: float = 0.0
    response_score: float = 0.0
    budget_match: float = 0.0
    confidence_penalty: float = 0.0
    final_score: float = 0.0


class EnhancedMatchResult(BaseModel):
    """增强版匹配结果"""
    opc: EnhancedOPCProfile
    score: float = 0.0
    detail: MatchDetail = Field(default_factory=MatchDetail)
    match_reasons: List[str] = Field(default_factory=list)
