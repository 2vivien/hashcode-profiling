from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from orientation.contracts.common import DataState, Observation

class StudentSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skill_id: str
    level: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    source: str
    status: str
    observed_at: datetime | None = None

class StudentProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    student_id: str
    profile_version: str = "v1"
    interests: dict[str,float] = Field(default_factory=dict)
    abilities: dict[str,float] = Field(default_factory=dict)
    values: dict[str,float] = Field(default_factory=dict)
    subjects: dict[str,float] = Field(default_factory=dict)
    skills: list[StudentSkill] = Field(default_factory=list)
    trajectory: dict[str,float] = Field(default_factory=dict)
    constraints: dict[str,str | float | bool | list[str] | DataState] = Field(default_factory=dict)
    observations: list[Observation] = Field(default_factory=list)
    generated_at: datetime | None = None
