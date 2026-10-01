from pathlib import Path

from fastapi import APIRouter

from orientation.assessment_v1.adaptive_bank import ADAPTIVE_BY_ID
from orientation.assessment_v1.engine import AssessmentV1Engine
from orientation.assessment_v1.models import AdaptiveQuestionRequest, AssessmentSubmission, LatentProfile, Question
from orientation.assessment_v1.service import AssessmentProfileService
from orientation.assessment_v1.telemetry import EventStore, EventType, JsonlEventStore, TelemetryEvent, make_event, reward_for
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(tags=["assessment-v1"])
service = AssessmentProfileService()
engine = AssessmentV1Engine()
event_store: EventStore = JsonlEventStore(
    Path("data/runtime/othello-orientation-events.jsonl")
)


class TelemetryIngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_type: EventType
    student_id: str = Field(min_length=1)
    session_id: str | None = None
    direction_id: str | None = None
    position: int | None = Field(default=None, ge=1)
    model_version: str | None = None
    questionnaire_version: str | None = None
    knowledge_version: str | None = None
    propensity: float | None = Field(default=None, gt=0, le=1)
    context: dict[str, float | str | bool] = {}
    payload: dict[str, str | int | float | bool | tuple[str, ...]] = {}


@router.get("/assessment-v1/questions", response_model=tuple[Question, ...])
def get_questions() -> tuple[Question, ...]:
    return service.questions()


@router.post("/assessment-v1/profile", response_model=LatentProfile)
def build_profile(submission: AssessmentSubmission) -> LatentProfile:
    return service.build_latent_profile(submission)


@router.post("/assessment-v1/adaptive", response_model=tuple[Question, ...])
def get_adaptive_questions(
    request: AdaptiveQuestionRequest,
    submission: AssessmentSubmission,
) -> tuple[Question, ...]:
    profile = service.build_latent_profile(submission)
    pairs = engine.adaptive_questions(profile, request)
    return tuple(ADAPTIVE_BY_ID[pair.question_id] for pair in pairs)


@router.post("/assessment-v1/telemetry", response_model=TelemetryEvent)
def ingest_telemetry(request: TelemetryIngestRequest) -> TelemetryEvent:
    event = make_event(
        request.event_type,
        request.student_id,
        session_id=request.session_id,
        direction_id=request.direction_id,
        position=request.position,
        model_version=request.model_version,
        questionnaire_version=request.questionnaire_version,
        knowledge_version=request.knowledge_version,
        propensity=request.propensity,
        context=request.context,
        payload=request.payload,
    )
    return event_store.append(event.model_copy(update={"reward": reward_for(event)}))
