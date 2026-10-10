from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from orientation.contracts.profile import StudentProfile
from orientation.occupation_knowledge.catalog import OccupationCatalog
from orientation.occupation_knowledge.models import DirectionExploration, OccupationMatch
from orientation.occupation_knowledge.scoring import OccupationScorer
from orientation.occupation_knowledge.training import TrainingRecommendation, load_training_catalog, recommend_training

router = APIRouter(tags=["occupation-v2"])


class OccupationRecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: StudentProfile
    limit: int = Field(default=20, ge=1, le=100)
    major_group: str | None = Field(default=None, pattern=r"^[0-9]$")


def _catalog_path() -> Path:
    configured = os.getenv("OTHELOO_OCCUPATION_CATALOG")
    if not configured:
        raise HTTPException(
            status_code=503,
            detail="occupation_catalog_not_configured",
        )
    return Path(configured)


@router.post("/occupation-v2/recommend", response_model=list[OccupationMatch])
def recommend_occupations(request: OccupationRecommendationRequest) -> list[OccupationMatch]:
    path = _catalog_path()
    if not path.is_file():
        raise HTTPException(status_code=503, detail="occupation_catalog_unavailable")
    catalog = OccupationCatalog.from_jsonl(path)
    records = list(catalog.records)
    if request.major_group is not None:
        records = [item for item in records if item.isco_major_group == request.major_group]
    if not records:
        raise HTTPException(status_code=404, detail="no_occupation_evidence")
    return OccupationScorer().rank(request.profile, records, request.limit)


@router.post("/occupation-v2/discover", response_model=list[DirectionExploration])
def discover_directions(request: OccupationRecommendationRequest) -> list[DirectionExploration]:
    path = _catalog_path()
    if not path.is_file():
        raise HTTPException(status_code=503, detail="occupation_catalog_unavailable")
    catalog = OccupationCatalog.from_jsonl(path)
    records = list(catalog.records)
    if request.major_group is not None:
        records = [item for item in records if item.isco_major_group == request.major_group]
    if not records:
        raise HTTPException(status_code=404, detail="no_occupation_evidence")
    return OccupationScorer().discover_directions(request.profile, records, min(request.limit, 20))


class TrainingRecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_ids: tuple[str, ...] = ()
    limit: int = Field(default=5, ge=1, le=20)


@router.post("/occupation-v2/training", response_model=list[TrainingRecommendation])
def recommend_training_opportunities(request: TrainingRecommendationRequest) -> list[TrainingRecommendation]:
    configured = os.getenv("OTHELOO_TRAINING_CATALOG")
    if not configured:
        raise HTTPException(status_code=503, detail="training_catalog_not_configured")
    path = Path(configured)
    if not path.is_file():
        raise HTTPException(status_code=503, detail="training_catalog_unavailable")
    catalog = load_training_catalog(path)
    return list(recommend_training({}, request.skill_ids, catalog, request.limit))
