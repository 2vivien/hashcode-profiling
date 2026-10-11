"""Périmètre géographique de la connaissance.

Un moteur d'orientation qui ne dit pas **quel pays** il couvre laisse croire
qu'il est universel. Cette version répond à la question : « de quelles données,
de quel pays, en quelle langue, sous quelle licence ? »

La réponse est lue depuis `data/catalog/coverage.json`, versionnée avec la
connaissance. Elle est exposée par `/system/info` et affichée dans l'interface.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

COVERAGE_PATH = Path("data/catalog/coverage.json")


@dataclass(frozen=True)
class Coverage:
    """Ce que couvre réellement une version de connaissance."""

    countries: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    country_names: dict[str, str] = field(default_factory=dict)
    authority: str = ""
    license: str = ""
    retrieved_at: str = ""
    knowledge_version: str = ""
    coverage_type: str = "national"
    completeness: str = "complete"
    note: str = ""

    @property
    def country_count(self) -> int:
        return len(self.countries)

    @property
    def is_national(self) -> bool:
        return self.coverage_type == "national"

    def describe(self) -> dict[str, Any]:
        return {
            "countries": list(self.countries),
            "country_names": dict(self.country_names),
            "country_count": self.country_count,
            "languages": list(self.languages),
            "authority": self.authority,
            "license": self.license,
            "retrieved_at": self.retrieved_at,
            "knowledge_version": self.knowledge_version,
            "type": self.coverage_type,
            "completeness": self.completeness,
            "note": self.note,
        }


def load_coverage(path: Path | None = None) -> Coverage:
    """Charge la couverture ; un fichier absent ne doit pas casser l'API."""
    target = path or COVERAGE_PATH
    if not target.is_file():
        return Coverage(note="couverture non renseignée")
    try:
        payload: dict[str, Any] = json.loads(target.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return Coverage(note="fichier de couverture illisible")

    raw_coverage = payload.get("coverage") or {}
    return Coverage(
        countries=tuple(payload.get("countries") or ()),
        languages=tuple(payload.get("languages") or ()),
        country_names={str(k): str(v) for k, v in (payload.get("country_names") or {}).items()},
        authority=str(payload.get("authority") or ""),
        license=str(payload.get("license") or ""),
        retrieved_at=str(payload.get("retrieved_at") or ""),
        knowledge_version=str(payload.get("version") or ""),
        coverage_type=str(raw_coverage.get("type") or "national"),
        completeness=str(raw_coverage.get("completeness") or "complete"),
        note=str(raw_coverage.get("note") or ""),
    )


@lru_cache(maxsize=4)
def _cached_coverage(knowledge_version: str) -> Coverage:
    return load_coverage()


def coverage_for(knowledge_version: str = "") -> Coverage:
    return _cached_coverage(knowledge_version)
