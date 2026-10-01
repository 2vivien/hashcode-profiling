from pydantic import BaseModel, ConfigDict, Field, model_validator


class Direction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    direction_id: str
    canonical_name: str
    aliases: list[str] = Field(default_factory=list)
    taxonomy: str
    interests: dict[str, float] = Field(default_factory=dict)
    abilities: dict[str, float] = Field(default_factory=dict)
    skills: dict[str, float] = Field(default_factory=dict)
    subjects: dict[str, float] = Field(default_factory=dict)
    values: dict[str, float] = Field(default_factory=dict)
    self_efficacy: dict[str, float] = Field(default_factory=dict)
    adaptability: dict[str, float] = Field(default_factory=dict)
    environment: dict[str, float] = Field(default_factory=dict)
    trajectory: dict[str, float] = Field(default_factory=dict)
    formations: list[str] = Field(default_factory=list)
    occupations: list[str] = Field(default_factory=list)
    requirements: dict[str, str | float | bool] = Field(default_factory=dict)
    accessibility: dict[str, str | float | bool] = Field(default_factory=dict)
    knowledge_version: str = "v1"

    @model_validator(mode="after")
    def validate_match_dimensions(self) -> "Direction":
        dimensions = (
            "interests",
            "abilities",
            "skills",
            "subjects",
            "values",
            "self_efficacy",
            "adaptability",
            "environment",
            "trajectory",
        )
        for name in dimensions:
            values = getattr(self, name)
            if any(value < 0 or value > 1 for value in values.values()):
                raise ValueError(f"{name} values must be normalized to [0,1]")
        if not self.direction_id.strip() or not self.canonical_name.strip():
            raise ValueError("direction_id and canonical_name are required")
        return self
