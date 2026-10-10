import os
from pathlib import Path

from fastapi import APIRouter

from orientation.api.routes.profiles import persist_profile, repository
from orientation.api.store import get_store
from orientation.application.use_cases.generate_recommendation import GenerateRecommendation
from orientation.config.settings import Settings
from orientation.contracts.profile import StudentProfile
from orientation.contracts.recommendation import Recommendation
from orientation.core.pipeline.orchestrator import PipelineOrchestrator
from orientation.infrastructure.knowledge.remote import RemoteKnowledge

router = APIRouter(tags=["recommendations"])

# Injection au démarrage — pas au niveau module global
_DEFAULT_KNOWLEDGE = Path(
    os.environ.get("DATA_PATH") or Path(__file__).resolve().parents[4] / "data" / "knowledge" / "v1"
)
_recommendation_service: GenerateRecommendation | None = None
_pipeline: PipelineOrchestrator | None = None


def init_pipeline(data_path: Path) -> PipelineOrchestrator:
    global _pipeline, _recommendation_service
    settings = Settings()
    remote = (
        RemoteKnowledge(settings.data_service_url, settings.knowledge_version)
        if settings.data_service_url
        else None
    )
    _recommendation_service = GenerateRecommendation(data_path, remote=remote)
    _pipeline = PipelineOrchestrator(_recommendation_service)
    return _pipeline


def get_service() -> GenerateRecommendation:
    """Service de recommandation (initialisé à la demande)."""
    service = _recommendation_service
    if service is None:
        init_pipeline(_DEFAULT_KNOWLEDGE)
        service = _recommendation_service
    if service is None:
        raise RuntimeError("recommendation_service_unavailable")
    return service


def _mirror(profile: StudentProfile, recommendation: Recommendation) -> None:
    """Persistance best-effort : mémoire + base. N'échoue jamais la réponse."""
    existing = repository.get(profile.student_id)
    if existing is None or existing.profile_version != profile.profile_version:
        repository.save(profile)
    persist_profile(profile)
    store = get_store()
    if store is not None:
        store.save_recommendation(profile, recommendation)


@router.post("/recommendations", response_model=Recommendation)
def generate_recommendation(profile: StudentProfile) -> Recommendation:
    pipeline = _pipeline or init_pipeline(_DEFAULT_KNOWLEDGE)
    recommendation = pipeline.execute(profile)
    _mirror(profile, recommendation)
    return recommendation
