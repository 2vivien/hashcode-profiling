from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from orientation.api.store import get_store
from orientation.contracts.common import Observation
from orientation.contracts.profile import StudentProfile
from orientation.domain.profile.evolution import ProfileEvolutionService
from orientation.infrastructure.persistence.profile_repository import InMemoryProfileRepository

router = APIRouter(tags=["profiles"])
repository = InMemoryProfileRepository()
evolution = ProfileEvolutionService()


def persist_profile(profile: StudentProfile) -> None:
    """Miroir best-effort vers la base — n'échoue jamais la requête."""
    store = get_store()
    if store is not None:
        store.save_profile(profile)


@router.post("/profiles", response_model=StudentProfile)
def create_profile(profile: StudentProfile) -> StudentProfile:
    saved = repository.save(profile)
    persist_profile(saved)
    return saved


@router.get("/profiles/{student_id}", response_model=StudentProfile)
def get_profile(student_id: str) -> StudentProfile:
    profile = repository.get(student_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="profile_not_found")
    return profile


@router.get("/profiles/{student_id}/history", response_model=list[StudentProfile])
def profile_history(student_id: str) -> list[StudentProfile]:
    return repository.history(student_id)


class EvolveRequest(BaseModel):
    observations: list[Observation] = Field(default_factory=list)


@router.post("/profiles/{student_id}/evolve", response_model=StudentProfile)
def evolve_profile(student_id: str, request: EvolveRequest) -> StudentProfile:
    """Applique des observations : fusion pondérée, version incrémentée."""
    profile = repository.get(student_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="profile_not_found")
    updated = evolution.apply_observations(profile, request.observations)
    saved = repository.save(updated)
    persist_profile(saved)
    return saved
