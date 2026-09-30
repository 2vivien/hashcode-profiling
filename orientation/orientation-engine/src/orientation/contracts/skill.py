from pydantic import BaseModel, Field


class SkillRequirement(BaseModel):
    skill_id: str
    required_level: float = Field(ge=0, le=1)


class SkillGap(BaseModel):
    skill_id: str
    current_level: float | None = Field(default=None, ge=0, le=1)
    required_level: float = Field(ge=0, le=1)
    gap: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    priority: float = Field(ge=0, le=1)
