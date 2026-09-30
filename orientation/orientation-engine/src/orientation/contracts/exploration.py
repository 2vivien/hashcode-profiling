from pydantic import BaseModel

class ExplorationIdea(BaseModel):
    exploration_id: str
    kind: str
    title: str
    purpose: str
    related_dimensions: list[str] = []
