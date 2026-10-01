from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from orientation.contracts.common import DataState, Observation, SourceType


class StudentSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skill_id: str
    level: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    source: str
    status: SourceType
    observed_at: datetime | None = None


class StudentProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    student_id: str
    profile_version: str = "v1"
    questionnaire_version: str | None = None
    assessment_confidence: float = Field(default=0.0, ge=0, le=1)
    riasec_entropy: float = Field(default=0.0, ge=0, le=1)
    contradictions: tuple[str, ...] = ()
    interests: dict[str, float] = Field(default_factory=dict)
    abilities: dict[str, float] = Field(default_factory=dict)
    values: dict[str, float] = Field(default_factory=dict)
    subjects: dict[str, float] = Field(default_factory=dict)
    self_efficacy: dict[str, float] = Field(default_factory=dict)
    adaptability: dict[str, float] = Field(default_factory=dict)
    environment: dict[str, float] = Field(default_factory=dict)
    skills: list[StudentSkill] = Field(default_factory=list)
    trajectory: dict[str, float] = Field(default_factory=dict)
    constraints: dict[str, str | float | bool | list[str] | DataState] = Field(default_factory=dict)
    observations: list[Observation] = Field(default_factory=list)
    generated_at: datetime | None = None

    @model_validator(mode="after")
    def validate_dimensions(self) -> "StudentProfile":
        dimensions = (
            "interests", "abilities", "values", "subjects", "self_efficacy",
            "adaptability", "environment", "trajectory",
        )
        for name in dimensions:
            values = getattr(self, name)
            if any(value < 0 or value > 1 for value in values.values()):
                raise ValueError(f"{name} values must be normalized to [0,1]")
        return self
