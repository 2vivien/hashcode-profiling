from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field

class SourceType(StrEnum):
    DECLARED = "declared"
    ASSESSED = "assessed"
    OBSERVED = "observed"
    INFERRED = "inferred"

class DataState(StrEnum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"
    CONTRADICTORY = "contradictory"

class Confidence(BaseModel):
    value: float = Field(ge=0, le=1)
    rationale: str = ""

class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dimension: str
    value: float | str | bool | list[str] | dict[str, float] | None
    confidence: float = Field(ge=0, le=1)
    source: SourceType
    state: DataState = DataState.KNOWN
    observed_at: datetime | None = None
    context: str | None = None
    version: str = "v1"
    provenance: str | None = None

