from datetime import datetime
from pydantic import BaseModel

class AuditSnapshot(BaseModel):
    request_id: str
    student_id: str
    profile_version: str
    assessment_version: str
    knowledge_version: str
    configuration_version: str
    feature_schema_version: str
    model_version: str
    candidate_set: list[str]
    ranking: list[str]
    scores: dict[str,float]
    uncertainty: dict[str,float]
    timestamp: datetime
