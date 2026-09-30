from pydantic import BaseModel, Field


class MatchResult(BaseModel):
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    evidence: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    interest_fit: float = Field(ge=0, le=1)
    ability_fit: float = Field(ge=0, le=1)
    skill_fit: float = Field(ge=0, le=1)
    value_fit: float = Field(ge=0, le=1)
    subject_fit: float = Field(ge=0, le=1)
    trajectory_fit: float = Field(ge=0, le=1)
    semantic_fit: float = Field(ge=0, le=1)
    graph_fit: float = Field(ge=0, le=1)
    skill_gap_penalty: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    compatibility: float = Field(ge=0, le=1)
