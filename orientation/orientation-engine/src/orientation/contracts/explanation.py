from pydantic import BaseModel

class ExplanationFact(BaseModel):
    kind: str
    dimension: str
    direction_id: str
    statement_key: str
    value: float | str | None = None
    evidence: list[str] = []

class Explanation(BaseModel):
    facts: list[ExplanationFact] = []
