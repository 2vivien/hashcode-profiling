from pydantic import BaseModel, Field

class ExplanationFact(BaseModel):
    kind: str
    dimension: str
    direction_id: str
    statement_key: str
    value: float | str | None = None
    evidence: list[str] = Field(default_factory=list)

class Explanation(BaseModel):
    facts: list[ExplanationFact] = Field(default_factory=list)
