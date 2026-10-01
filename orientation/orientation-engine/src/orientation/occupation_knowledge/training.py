from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class TrainingOpportunity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_id: str
    title: str
    provider: str
    occupation_ids: tuple[str, ...] = ()
    skill_ids: tuple[str, ...] = ()
    level: str | None = None
    duration_hours: float | None = Field(default=None, ge=0)
    location: str | None = None
    url: str | None = None
    source_version: str
    provenance: tuple[str, ...] = ()


class TrainingRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_id: str
    title: str
    provider: str
    relevance: float = Field(ge=0, le=1)
    matched_skills: tuple[str, ...] = ()
    missing_skills: tuple[str, ...] = ()
    rationale: str


def load_training_catalog(path: Path) -> tuple[TrainingOpportunity, ...]:
    records: list[TrainingOpportunity] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(TrainingOpportunity.model_validate(json.loads(line)))
    return tuple(records)


def recommend_training(
    profile_skill_levels: dict[str, float],
    required_skill_ids: tuple[str, ...],
    opportunities: tuple[TrainingOpportunity, ...],
    limit: int = 5,
) -> tuple[TrainingRecommendation, ...]:
    required = set(required_skill_ids)
    ranked: list[TrainingRecommendation] = []
    for opportunity in opportunities:
        matched = tuple(sorted(required & set(opportunity.skill_ids)))
        missing = tuple(sorted(required - set(opportunity.skill_ids)))
        relevance = len(matched) / max(1, len(required))
        if not matched:
            continue
        ranked.append(
            TrainingRecommendation(
                opportunity_id=opportunity.opportunity_id,
                title=opportunity.title,
                provider=opportunity.provider,
                relevance=relevance,
                matched_skills=matched,
                missing_skills=missing,
                rationale=f"{len(matched)} compétence(s) cible(s) couverte(s) par cette opportunité.",
            )
        )
    ranked.sort(key=lambda item: (-item.relevance, item.title))
    return tuple(ranked[:limit])
