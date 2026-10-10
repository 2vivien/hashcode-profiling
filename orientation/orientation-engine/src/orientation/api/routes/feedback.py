from fastapi import APIRouter

from orientation.api.routes.profiles import persist_profile, repository
from orientation.api.routes.recommendations import get_service
from orientation.api.store import get_store
from orientation.contracts.feedback import FeedbackEvent
from orientation.domain.profile.evolution import ProfileEvolutionService

router = APIRouter(tags=["feedback"])
evolution = ProfileEvolutionService()

# Un clic n'apprend rien : seul un signal d'intention fait évoluer le profil.
FEEDBACK_KIND: dict[str, str] = {
    "save": "pertinent",
    "explore": "pertinent",
    "complete_exploration": "pertinent",
    "request_detail": "pertinent",
    "reject": "pas_pertinent",
}


def _evolve(event: FeedbackEvent) -> str | None:
    kind = FEEDBACK_KIND.get(event.event_type)
    profile = repository.get(event.student_id)
    if kind is None or profile is None:
        return None
    bundle = get_service().knowledge()
    direction = next((item for item in bundle.directions if item.direction_id == event.direction_id), None)
    if direction is None:
        return None
    updated = evolution.apply_feedback(profile, kind, direction)
    repository.save(updated)
    persist_profile(updated)
    return updated.profile_version


@router.post("/feedback", response_model=FeedbackEvent)
def record_feedback(event: FeedbackEvent) -> FeedbackEvent:
    profile_version = _evolve(event)
    store = get_store()
    if store is not None:
        store.save_feedback(
            {
                "studentRef": event.student_id,
                "directionId": event.direction_id,
                "type": event.event_type,
                "payload": {
                    "eventId": event.event_id,
                    "value": event.value,
                    "occurredAt": event.occurred_at,
                    "profileVersion": profile_version,
                    **event.context,
                },
            }
        )
    if profile_version is not None:
        return event.model_copy(update={"profile_version": profile_version})
    return event
