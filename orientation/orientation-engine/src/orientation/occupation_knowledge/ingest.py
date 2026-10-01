from __future__ import annotations

import csv
from pathlib import Path
from collections.abc import Iterable

from orientation.occupation_knowledge.models import OccupationRecord
from orientation.occupation_knowledge.taxonomy import major_group


def _first(row: dict[str, str], *names: str) -> str:
    for name in names:
        value = row.get(name)
        if value:
            return value.strip()
    return ""


def _group_for(code: str) -> tuple[str | None, tuple[str, ...]]:
    group = major_group(code)
    return (group.code, (group.name_fr,)) if group else (None, ())


def read_esco_occupations(path: Path, version: str = "v1.2.1") -> list[OccupationRecord]:
    records: list[OccupationRecord] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            uri = _first(row, "conceptUri", "URI", "uri")
            title = _first(row, "preferredLabel", "preferredTerm", "title")
            if not uri or not title:
                continue
            code = _first(row, "iscoCode", "ISCO08Code", "ISCO-08 code")
            group_code, domains = _group_for(code)
            aliases = tuple(
                value.strip()
                for value in _first(row, "altLabels", "alternativeLabels").split("|")
                if value.strip()
            )
            records.append(
                OccupationRecord(
                    occupation_id=f"esco:{uri}",
                    source="esco",
                    source_version=version,
                    title=title,
                    description=_first(row, "description", "scopeNote"),
                    aliases=aliases,
                    isco08_code=code or None,
                    isco_major_group=group_code,
                    domains=domains,
                    evidence_count=1,
                    data_completeness=0.35 if code else 0.20,
                )
            )
    return records


def read_onet_occupation_data(path: Path, version: str = "31.0") -> list[OccupationRecord]:
    records: list[OccupationRecord] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            code = _first(row, "O*NET-SOC Code", "O*NET-SOC_Code")
            title = _first(row, "Title")
            if not code or not title:
                continue
            records.append(
                OccupationRecord(
                    occupation_id=f"onet:{code}",
                    source="onet",
                    source_version=version,
                    title=title,
                    description=_first(row, "Description"),
                    evidence_count=1,
                    data_completeness=0.25,
                )
            )
    return records


def merge_records(records: Iterable[OccupationRecord]) -> list[OccupationRecord]:
    by_title: dict[str, OccupationRecord] = {}
    for record in records:
        key = record.title.casefold().strip()
        current = by_title.get(key)
        if current is None:
            by_title[key] = record
            continue
        if current.source == "esco" and record.source == "onet":
            by_title[key] = current.model_copy(
                update={
                    "source": "merged",
                    "evidence_count": current.evidence_count + record.evidence_count,
                    "data_completeness": max(current.data_completeness, record.data_completeness),
                    "isco08_code": current.isco08_code or record.isco08_code,
                    "isco_major_group": current.isco_major_group or record.isco_major_group,
                }
            )
    return sorted(by_title.values(), key=lambda item: item.title.casefold())
