from pydantic import BaseModel, ConfigDict, Field

class Direction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    direction_id: str
    canonical_name: str
    aliases: list[str] = Field(default_factory=list)
    taxonomy: str
    interests: dict[str,float] = Field(default_factory=dict)
    abilities: dict[str,float] = Field(default_factory=dict)
    skills: dict[str,float] = Field(default_factory=dict)
    subjects: dict[str,float] = Field(default_factory=dict)
    values: dict[str,float] = Field(default_factory=dict)
    formations: list[str] = Field(default_factory=list)
    occupations: list[str] = Field(default_factory=list)
    requirements: dict[str,str | float | bool] = Field(default_factory=dict)
    accessibility: dict[str,str | float | bool] = Field(default_factory=dict)
    knowledge_version: str = "v1"
