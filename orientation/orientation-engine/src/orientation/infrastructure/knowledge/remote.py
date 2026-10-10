"""Source de connaissance distante (data-service Drizzle), avec cache et repli JSON."""

from __future__ import annotations

import json
import time
from typing import Any, TypeVar, cast
from urllib import error, request

from pydantic import BaseModel

from orientation.contracts.direction import Direction
from orientation.contracts.formation import Formation
from orientation.occupation_knowledge.models import OccupationRecord

T = TypeVar("T", bound=BaseModel)

_DIRECTIONS = "directions"
_OCCUPATIONS = "occupations"
_FORMATIONS = "formations"


class RemoteKnowledge:
    """Lit la connaissance depuis le data-service, avec cache mémoire TTL.

    Retourne ``None`` en cas d'indisponibilité : l'appelant garde le repli JSON.
    """

    def __init__(self, base_url: str, version: str, timeout: float = 2.0, ttl: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.version = version
        self.timeout = timeout
        self.ttl = ttl
        self._cache: dict[str, tuple[float, list[Any]]] = {}

    def _rows(self, resource: str) -> list[dict[str, Any]] | None:
        url = f"{self.base_url}/knowledge/{resource}?version={self.version}"
        try:
            with request.urlopen(url, timeout=self.timeout) as response:  # nosec B310
                payload = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError):
            return None
        if not isinstance(payload, list):
            return None
        return [row for row in payload if isinstance(row, dict)]

    def _models(self, resource: str, model: type[T]) -> list[T] | None:
        now = time.monotonic()
        cached = self._cache.get(resource)
        if cached is not None and now - cached[0] < self.ttl:
            return cast("list[T]", cached[1])

        rows = self._rows(resource)
        if rows is None:
            return None
        try:
            models: list[T] = [model.model_validate(row["data"]) for row in rows]
        except (KeyError, TypeError, ValueError):
            return None
        if not models:
            return None

        self._cache[resource] = (now, list(models))
        return models

    def directions(self) -> list[Direction] | None:
        return self._models(_DIRECTIONS, Direction)

    def occupations(self) -> list[OccupationRecord] | None:
        return self._models(_OCCUPATIONS, OccupationRecord)

    def formations(self) -> list[Formation] | None:
        return self._models(_FORMATIONS, Formation)
