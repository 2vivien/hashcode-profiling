from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

EventType = Literal[
    "QUESTIONNAIRE_STARTED", "QUESTIONNAIRE_COMPLETED", "ADAPTIVE_QUESTION_SHOWN",
    "DIRECTION_CLICKED", "JOB_DETAIL_DWELL_TIME", "JOB_FAVORITED", "JOB_COMPARED",
    "FORMATION_CLICKED", "FORMATION_STARTED", "FORMATION_COMPLETED", "USER_FEEDBACK_GIVEN",
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
    def append(self, event: TelemetryEvent) -> TelemetryEvent: ...


class JsonlEventStore:
    """Append-only event store with a tamper-evident hash chain."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._previous_hash = self._last_hash()

    def _last_hash(self) -> str:
        if not self.path.exists():
            return "GENESIS"
        lines = [line for line in self.path.read_text(encoding="utf-8").splitlines() if line]
        return str(json.loads(lines[-1])["context"]["chain_hash"]) if lines else "GENESIS"

    def append(self, event: TelemetryEvent) -> TelemetryEvent:
        base = event.model_dump(mode="json")
        canonical = json.dumps(base, sort_keys=True, separators=(",", ":"))
        chain_hash = hashlib.sha256((self._previous_hash + canonical).encode("utf-8")).hexdigest()
        context = dict(event.context)
        context["chain_hash"] = chain_hash
        stored = event.model_copy(update={"context": context})
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(stored.model_dump_json() + "\n")
            handle.flush()
        self._previous_hash = chain_hash
        return stored

    def verify_chain(self) -> bool:
        previous = "GENESIS"
        if not self.path.exists():
            return True
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            if not raw:
                continue
            record = json.loads(raw)
            observed = record.get("context", {}).get("chain_hash")
            context = dict(record.get("context", {}))
            context.pop("chain_hash", None)
            record["context"] = context
            canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
            expected = hashlib.sha256((previous + canonical).encode("utf-8")).hexdigest()
            if observed != expected:
                return False
            previous = expected
        return True


def make_event(event_type: EventType, student_id: str, **kwargs: object) -> TelemetryEvent:
    now = datetime.now(timezone.utc)
    seed = f"{student_id}:{event_type}:{now.isoformat()}"
    return TelemetryEvent(
        event_id=hashlib.sha256(seed.encode("utf-8")).hexdigest()[:32],
        event_type=event_type,
        student_id=student_id,
        occurred_at=now,
        **kwargs,
    )


def reward_for(event: TelemetryEvent) -> float:
    weights: dict[str, float] = {
        "QUESTIONNAIRE_COMPLETED": 0.05, "DIRECTION_CLICKED": 0.10,
        "JOB_DETAIL_DWELL_TIME": 0.15, "JOB_FAVORITED": 0.35,
        "JOB_COMPARED": 0.20, "FORMATION_CLICKED": 0.20,
        "FORMATION_STARTED": 0.65, "FORMATION_COMPLETED": 1.00,
        "USER_FEEDBACK_GIVEN": 0.70, "REAL_CHOICE_DECLARED": 1.00,
    }
    if event.event_type == "USER_FEEDBACK_GIVEN":
        return max(-1.0, min(1.0, float(event.payload.get("feedback", 0))))
    if event.event_type == "JOB_DETAIL_DWELL_TIME":
        seconds = max(0.0, float(event.payload.get("seconds", 0)))
        return min(1.0, seconds / 180.0) * weights[event.event_type]
    return weights.get(event.event_type, 0.0)
