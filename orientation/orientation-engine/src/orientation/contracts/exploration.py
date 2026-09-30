from pydantic import BaseModel, Field


class ExplorationIdea(BaseModel):
    exploration_id: str
    kind: str
    title: str
    purpose: str
    related_dimensions: list[str] = Field(default_factory=list)
