from typing import Literal

from pydantic import BaseModel, Field

FeedbackEventType = Literal[
    "view",
    "save",
    "reject",
    "explore",
    "complete_exploration",
    "request_detail",
]


class FeedbackEvent(BaseModel):
    event_id: str
    student_id: str
    direction_id: str
    event_type: FeedbackEventType
    value: float = Field(default=1.0, ge=-1, le=1)
    occurred_at: str
    context: dict[str, str] = Field(default_factory=dict)
