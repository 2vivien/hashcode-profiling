from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class AssessmentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    assessment_id: str
    session_id: str
    instrument_version: str
    traits: dict[str, float]
    theta: dict[str, float] = {}
    standard_error: dict[str, float] = {}
    information: dict[str, float] = {}
    responses_count: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    completed_at: datetime
