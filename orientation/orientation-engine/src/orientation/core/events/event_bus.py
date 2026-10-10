from __future__ import annotations

from collections.abc import Callable
from typing import Any

Handler = Callable[[Any], None]


class EventBus:
    """Bus minimal — permet aux outils externes (audit, formation) de s'abonner sans polling."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = {}

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event: Any) -> None:
        event_type = event.__class__.__name__
        for handler in self._subscribers.get(event_type, []):
            handler(event)
