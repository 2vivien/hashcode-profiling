from pydantic import BaseModel, ConfigDict, Field

class Direction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    direction_id: str
    canonical_name: str
    aliases: list[str] = []
    taxonomy: str
    interests: dict[str, float] = {}
    abilities: dict[str, float] = {}
    skills: dict[str, float] = {}
    subjects: dict[str, float] = {}
    values: dict[str, float] = {}
    formations: list[str] = []
    occupations: list[str] = []
    requirements: dict[str, str | float | bool] = {}
    accessibility: dict[str, str | float | bool] = {}
    knowledge_version: str = "v1"
