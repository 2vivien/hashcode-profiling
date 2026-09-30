from fastapi import APIRouter

from orientation.contracts.feedback import FeedbackEvent

router = APIRouter(tags=["feedback"])


@router.post("/feedback", response_model=FeedbackEvent)
def record_feedback(event: FeedbackEvent) -> FeedbackEvent:
    return event
