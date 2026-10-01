from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SourceName = Literal["esco", "onet", "isco", "merged"]


class OccupationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    occupation_id: str
    source: SourceName
    source_version: str
    title: str
    description: str = ""
    aliases: tuple[str, ...] = ()
    isco08_code: str | None = None
    isco_major_group: str | None = None
    domains: tuple[str, ...] = ()
    riasec: dict[str, float] = Field(default_factory=dict)
    abilities: dict[str, float] = Field(default_factory=dict)
    skills: dict[str, float] = Field(default_factory=dict)
    values: dict[str, float] = Field(default_factory=dict)
    knowledge: dict[str, float] = Field(default_factory=dict)
    work_style: dict[str, float] = Field(default_factory=dict)
    environment: dict[str, float] = Field(default_factory=dict)
    work_activities: dict[str, float] = Field(default_factory=dict)
    training: dict[str, float] = Field(default_factory=dict)
    education_level: float | None = Field(default=None, ge=0, le=1)
    job_zone: int | None = Field(default=None, ge=1, le=5)
    onet_soc_code: str | None = None
    esco_uri: str | None = None
    skill_ids: tuple[str, ...] = ()
    skill_labels: dict[str, str] = Field(default_factory=dict)
    essential_skill_ids: tuple[str, ...] = ()
    optional_skill_ids: tuple[str, ...] = ()
    task_terms: tuple[str, ...] = ()
    related_occupation_ids: tuple[str, ...] = ()
    broader_occupation_ids: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    evidence_count: int = Field(default=0, ge=0)
    data_completeness: float = Field(default=0.0, ge=0, le=1)


class ScoreComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    score: float = Field(ge=0, le=1)
    weight: float = Field(ge=0, le=1)
    evidence: tuple[str, ...] = ()


class OccupationMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    occupation_id: str
    title: str
    source: str
    score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    uncertainty: float = Field(default=0.0, ge=0, le=1)
    recommendation_class: Literal["strong_fit", "good_fit", "adjacent", "exploration"] = "exploration"
    isco08_code: str | None = None
    isco_major_group: str | None = None
    components: tuple[ScoreComponent, ...] = ()
    reasons: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    experiences: tuple[str, ...] = ()
    related_occupation_ids: tuple[str, ...] = ()
    evidence_count: int = Field(default=0, ge=0)
    provenance: tuple[str, ...] = ()


class DirectionExploration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    direction_id: str
    label: str
    compatibility: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    uncertainty: float = Field(ge=0, le=1)
    reasons: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    experiences: tuple[str, ...] = ()
    candidate_occupation_ids: tuple[str, ...] = ()
