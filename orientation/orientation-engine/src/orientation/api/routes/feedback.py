from fastapi import APIRouter
from pydantic import BaseModel, Field
router=APIRouter(tags=["feedback"])

class FeedbackEvent(BaseModel):
    event_id:str
    student_id:str
    direction_id:str
    event_type:str
    value:float=Field(default=1.0,ge=-1,le=1)
    occurred_at:str
    context:dict[str,str]=Field(default_factory=dict)

@router.post("/feedback",response_model=FeedbackEvent)
def record_feedback(event:FeedbackEvent)->FeedbackEvent:
    return event
