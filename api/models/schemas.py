"""Pydantic 数据模型 —— 请求/响应 schema"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ─── 请求模型 ───────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' 或 'assistant'")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="会话 ID")
    messages: List[ChatMessage] = Field(..., description="对话历史（包括最新消息）")
    user_id: Optional[str] = Field(None, description="用户 ID（可选）")


class MatchRequest(BaseModel):
    session_id: str = Field(..., description="会话 ID")
    user_id: Optional[str] = Field(None, description="用户 ID")


# ─── 响应模型 ───────────────────────────────────────────

class DemandProfileOut(BaseModel):
    session_id: str
    project_type: str = ""
    project_scope: str = Field(default="", description="项目规模/范围，如'两个页面''完整小程序'等")
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    timeline: str = ""
    skills_required: List[str] = Field(default_factory=list)
    target_users: str = Field(default="", description="目标用户群体")
    constraints: str = Field(default="", description="特殊约束或要求")
    description: str = ""
    # 「找人」维度新增字段
    collaboration_mode: str = Field(default="", description="协作方式：远程/线下/混合")
    industry: str = Field(default="", description="行业领域，如'电商''教育''金融'")
    service_expectations: str = Field(default="", description="对 OPC 的核心期望，如'经验丰富''响应快''性价比高'")
    is_complete: bool = False
    missing_fields: List[str] = Field(default_factory=list)


class OPCMatch(BaseModel):
    id: str
    name: str
    avatar_url: Optional[str]
    role: str
    description: Optional[str]
    skills: List[str] = Field(default_factory=list)
    match_rate: float = Field(..., description="匹配度 0-100")
    match_reasons: List[str] = Field(default_factory=list, description="匹配理由")
    is_available: bool = True


class ChatResponse(BaseModel):
    session_id: str
    assistant_message: str = Field(..., description="AI 回复内容")
    demand_profile: Optional[DemandProfileOut] = Field(None, description="需求画像（有更新时返回）")
    matches: List[OPCMatch] = Field(default_factory=list, description="匹配结果（需求完整时返回）")
    is_matching_complete: bool = False


class MatchResponse(BaseModel):
    session_id: str
    demand_profile: DemandProfileOut
    matches: List[OPCMatch]
