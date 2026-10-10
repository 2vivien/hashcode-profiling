from datetime import datetime

from pydantic import BaseModel


class ProfileUpdated(BaseModel):
    student_id: str
    profile_version: str
    timestamp: datetime
    source: str  # questionnaire, observation, inference


class FeedbackReceived(BaseModel):
    student_id: str
    direction_id: str
    feedback_type: str  # pertinent / pas_pertinent / interessante / rejete
    timestamp: datetime


class RecommendationGenerated(BaseModel):
    student_id: str
    recommendation_version: str
    direction_ids: list[str]
    model_version: str
    knowledge_version: str
    timestamp: datetime


class AuditFairnessRequested(BaseModel):
    student_id: str | None
    audit_type: str  # demographic_parity / equal_opportunity
    timestamp: datetime
