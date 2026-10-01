from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from orientation.contracts.profile import StudentProfile
from orientation.occupation_knowledge.catalog import OccupationCatalog
from orientation.occupation_knowledge.models import OccupationMatch
from orientation.occupation_knowledge.scoring import OccupationScorer

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
