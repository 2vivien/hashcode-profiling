from fastapi import APIRouter

from orientation.assessment_v1.adaptive_bank import ADAPTIVE_BY_ID
from orientation.assessment_v1.engine import AssessmentV1Engine
from orientation.assessment_v1.models import AdaptiveQuestionRequest, AssessmentSubmission, LatentProfile, Question
from orientation.assessment_v1.service import AssessmentProfileService
from orientation.assessment_v1.telemetry import EventType, EventStore, TelemetryEvent, make_event, reward_for

router = APIRouter(tags=["assessment-v1"])
service = AssessmentProfileService()
engine = AssessmentV1Engine()


@router.get("/assessment-v1/questions", response_model=tuple[Question, ...])
def get_questions() -> tuple[Question, ...]:
    return tuple(service.questions())


@router.post("/assessment-v1/profile", response_model=LatentProfile)
def build_profile(submission: AssessmentSubmission) -> LatentProfile:
    return service.build_latent_profile(submission)


@router.post("/assessment-v1/adaptive", response_model=tuple[Question, ...])
def get_adaptive_questions(request: AdaptiveQuestionRequest, submission: AssessmentSubmission) -> tuple[Question, ...]:
    profile = service.build_latent_profile(submission)
    pairs = engine.adaptive_questions(profile, request)
    return tuple(ADAPTIVE_BY_ID[pair.question_id] for pair in pairs)


class TelemetryService:
    def __init__(self, store: EventStore) -> None:
        self.store = store

    def record(self, event_type: EventType, student_id: str, **kwargs: object) -> TelemetryEvent:
        event = make_event(event_type, student_id, **kwargs)
        return self.store.append(event.model_copy(update={"reward": reward_for(event)}))
