from pydantic import BaseModel

class Candidate(BaseModel):
    direction_id: str
    generation_sources: list[str] = []
    constraint_status: str = "unknown"
    knowledge_evidence: list[str] = []
