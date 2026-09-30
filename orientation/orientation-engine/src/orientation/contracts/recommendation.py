from datetime import datetime
from pydantic import BaseModel, Field
from orientation.contracts.audit import AuditSnapshot
from orientation.contracts.explanation import Explanation
from orientation.contracts.exploration import ExplorationIdea
from orientation.contracts.scoring import ScoreBreakdown
from orientation.contracts.skill import SkillGap

class RecommendationItem(BaseModel):
    direction_id: str
    direction_name: str
    taxonomy: str
    score: float = Field(ge=0,le=1)
    confidence: float = Field(ge=0,le=1)
    uncertainty: float = Field(ge=0,le=1)
    score_breakdown: ScoreBreakdown
    skill_gaps: list[SkillGap] = []
    explanation: Explanation = Explanation()
    explorations: list[ExplorationIdea] = []

class Recommendation(BaseModel):
    recommendation_id: str
    profile_version: str
    model_version: str
    knowledge_version: str
    candidates: list[RecommendationItem]
    created_at: datetime
    audit: AuditSnapshot
