from pydantic import BaseModel, ConfigDict, Field


class Formation(BaseModel):
    """Formation (parcours) rattachable à une direction."""

    model_config = ConfigDict(extra="forbid")

    formation_id: str
    title: str
    level: float = Field(default=0.5, ge=0, le=1)
    duration_years: int | None = Field(default=None, ge=0, le=12)
    fields: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    description: str = ""
    knowledge_version: str = "v1"
