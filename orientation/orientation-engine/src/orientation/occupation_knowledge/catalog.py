from __future__ import annotations

import json
from pathlib import Path

from orientation.occupation_knowledge.models import OccupationRecord


class OccupationCatalog:
    def __init__(self, records: list[OccupationRecord]) -> None:
        if len({record.occupation_id for record in records}) != len(records):
            raise ValueError("occupation ids must be unique")
        self.records = tuple(records)

    @classmethod
    def from_jsonl(cls, path: Path) -> "OccupationCatalog":
        records: list[OccupationRecord] = []
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(OccupationRecord.model_validate(json.loads(line)))
        return cls(records)

    def by_major_group(self, group: str) -> tuple[OccupationRecord, ...]:
        return tuple(item for item in self.records if item.isco_major_group == group)

    def search(self, query: str, limit: int = 20) -> tuple[OccupationRecord, ...]:
        normalized = query.casefold().strip()
        if not normalized:
            return ()
        scored = []
        for item in self.records:
            haystack = " ".join((item.title, item.description, *item.aliases)).casefold()
            terms = normalized.split()
            overlap = sum(term in haystack for term in terms)
            if overlap:
                scored.append((overlap, item))
        scored.sort(key=lambda pair: (-pair[0], pair[1].title))
        return tuple(item for _, item in scored[:limit])
