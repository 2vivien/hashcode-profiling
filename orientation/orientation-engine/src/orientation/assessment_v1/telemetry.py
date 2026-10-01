from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field


EventType = Literal[
    "QUESTIONNAIRE_STARTED",
    "QUESTIONNAIRE_COMPLETED",
    "ADAPTIVE_QUESTION_SHOWN",
    "DIRECTION_CLICKED",
    "JOB_DETAIL_DWELL_TIME",
    "JOB_FAVORITED",
    "JOB_COMPARED",
    "FORMATION_CLICKED",
    "FORMATION_STARTED",
    "FORMATION_COMPLETED",
    "USER_FEEDBACK_GIVEN",
    "REAL_CHOICE_DECLARED",
]


class TelemetryEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    event_id: str
    event_type: EventType
    student_id: str
    occurred_at: datetime
    session_id: str | None = None
    direction_id: str | None = None
    position: int | None = Field(default=None, ge=1)
    model_version: str | None = None
    questionnaire_version: str | None = None
    knowledge_version: str | None = None
    propensity: float | None = Field(default=None, gt=0, le=1)
    reward: float | None = Field(default=None, ge=-1, le=1)
    context: dict[str, float | str | bool] = Field(default_factory=dict)
    payload: dict[str, str | int | float | bool | tuple[str, ...]] = Field(default_factory=dict)


class EventStore(Protocol):
    def append(self, event: TelemetryEvent) -> None: ...


class JsonlEventStore:
    """Append-only store. Existing records are never rewritten or deleted."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: TelemetryEvent) -> None:
        line = event.model_dump_json() + "\n"
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()

    def verify_chain(self) -> bool:
        previous = "GENESIS"
        if not self.path.exists():
            return True
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            if not raw:
                continue
            record = json.loads(raw)
            expected = hashlib.sha256((previous + raw).encode("utf-8")).hexdigest()
            if record.get("context", {}).get("chain_hash") != expected:
                return False
            previous = expected
        return True


def make_event(event_type: EventType, student_id: str, **kwargs: object) -> TelemetryEvent:
    return TelemetryEvent(
        event_id=hashlib.sha256(f"{student_id}:{event_type}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:32],
        event_type=event_type,
        student_id=student_id,
        occurred_at=datetime.now(timezone.utc),
        **kwargs,
    )


def reward_for(event: TelemetryEvent) -> float:
    weights: dict[str, float] = {
        "QUESTIONNAIRE_COMPLETED": 0.05,
        "DIRECTION_CLICKED": 0.10,
        "JOB_DETAIL_DWELL_TIME": 0.15,
        "JOB_FAVORITED": 0.35,
        "JOB_COMPARED": 0.20,
        "FORMATION_CLICKED": 0.20,
        "FORMATION_STARTED": 0.65,
        "FORMATION_COMPLETED": 1.00,
        "USER_FEEDBACK_GIVEN": 0.70,
        "REAL_CHOICE_DECLARED": 1.00,
    }
    base = weights.get(event.event_type, 0.0)
    if event.event_type == "USER_FEEDBACK_GIVEN":
        return max(-1.0, min(1.0, float(event.payload.get("feedback", 0))))
    if event.event_type == "JOB_DETAIL_DWELL_TIME":
        seconds = float(event.payload.get("seconds", 0))
        return min(1.0, seconds / 180.0) * base
    return base
