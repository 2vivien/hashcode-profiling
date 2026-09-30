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
    interests: dict[str, float] = {}
    abilities: dict[str, float] = {}
    values: dict[str, float] = {}
    subjects: dict[str, float] = {}
    skills: list[StudentSkill] = []
    trajectory: dict[str, float] = {}
    constraints: dict[str, str | float | bool | list[str] | DataState] = {}
    observations: list[Observation] = []
    generated_at: datetime | None = None
