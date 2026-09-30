from pydantic import BaseModel, Field


class Candidate(BaseModel):
    direction_id: str
    generation_sources: list[str] = Field(default_factory=list)
    constraint_status: str = "unknown"
    knowledge_evidence: list[str] = Field(default_factory=list)
