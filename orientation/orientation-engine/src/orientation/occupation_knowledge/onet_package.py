from __future__ import annotations

import csv
import io
import zipfile
from collections import defaultdict
from pathlib import Path

from orientation.occupation_knowledge.models import OccupationRecord


def _open_rows(archive: zipfile.ZipFile, suffixes: tuple[str, ...]) -> list[dict[str, str]]:
    name = next((item for item in archive.namelist() if item.lower().endswith(tuple(s.lower() for s in suffixes))), None)
    if name is None:
        return []
    with archive.open(name) as raw:
        return list(csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig"), delimiter="	"))


def _number(row: dict[str, str]) -> float | None:
    raw = (row.get("Data Value") or row.get("DataValue") or row.get("value") or "").strip()
    try:
        return float(raw)
    except ValueError:
        return None


def _aggregate(rows: list[dict[str, str]], max_items: int = 80) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = defaultdict(dict)
    for row in rows:
        code = (row.get("O*NET-SOC Code") or "").strip()
        if not code:
            continue
        name = (row.get("Element Name") or row.get("Scale Name") or row.get("Content Model Element") or "").strip()
        value = _number(row)
        if name and value is not None and len(result[code]) < max_items:
            result[code][name] = value
    return dict(result)


def _aggregate_normalized(rows: list[dict[str, str]], max_items: int = 80) -> dict[str, dict[str, float]]:
    raw = _aggregate(rows, max_items)
    normalized: dict[str, dict[str, float]] = {}
    for code, values in raw.items():
        normalized[code] = {
            key: max(0.0, min(1.0, value / (100.0 if value > 7.0 else 7.0)))
            for key, value in values.items()
        }
    return normalized


def _job_zones(rows: list[dict[str, str]]) -> dict[str, int]:
    result: dict[str, int] = {}
    for row in rows:
        code = (row.get("O*NET-SOC Code") or "").strip()
        raw = (row.get("Job Zone") or "").strip()
        try:
            zone = int(float(raw))
        except ValueError:
            continue
        if code and 1 <= zone <= 5:
            result[code] = zone
    return result


def _relations(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        code = (row.get("O*NET-SOC Code") or "").strip()
        related = (row.get("Related O*NET-SOC Code") or row.get("Related Occupation") or "").strip()
        if code and related and related != code:
            result[code].append(related)
    return result


def _tasks(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        code = (row.get("O*NET-SOC Code") or "").strip()
        task = (row.get("Task") or row.get("Task Statement") or "").strip()
        if code and task and len(result[code]) < 12:
            result[code].append(task)
    return result


def read_onet_zip(path: Path, version: str = "31.0") -> list[OccupationRecord]:
    """Read O*NET 31.0 tabular data and preserve evidence by occupation.

    The parser is deliberately tolerant of optional files: a partial archive is
    accepted, but its data_completeness reflects what was actually present.
    """
    with zipfile.ZipFile(path) as archive:
        occupations = _open_rows(archive, ("Occupation Data.txt", "Occupation Data.csv"))
        abilities = _aggregate_normalized(_open_rows(archive, ("Abilities.txt",)))
        skills = _aggregate_normalized(_open_rows(archive, ("Skills.txt",)))
        knowledge = _aggregate_normalized(_open_rows(archive, ("Knowledge.txt",)))
        interests = _aggregate_normalized(_open_rows(archive, ("Interests.txt",)))
        work_styles = _aggregate_normalized(_open_rows(archive, ("Work Styles.txt",)))
        activities = _aggregate_normalized(_open_rows(archive, ("Work Activities.txt",)))
        education = _aggregate_normalized(_open_rows(archive, ("Education, Training, and Experience.txt", "Education, Training, and Experience.csv")))
        zones = _job_zones(_open_rows(archive, ("Job Zones.txt",)))
        related = _relations(_open_rows(archive, ("Related Occupations.txt",)))
        tasks = _tasks(_open_rows(archive, ("Task Statements.txt",)))

    records: list[OccupationRecord] = []
    for row in occupations:
        code = (row.get("O*NET-SOC Code") or "").strip()
        title = (row.get("Title") or "").strip()
        if not code or not title:
            continue
        evidence_sets = (abilities, skills, knowledge, interests, work_styles, activities, education)
        present = sum(bool(values.get(code)) for values in evidence_sets)
        records.append(
            OccupationRecord(
                occupation_id=f"onet:{code}",
                source="onet",
                source_version=version,
                title=title,
                description=(row.get("Description") or "").strip(),
                onet_soc_code=code,
                riasec=interests.get(code, {}),
                abilities=abilities.get(code, {}),
                skills=skills.get(code, {}),
                knowledge=knowledge.get(code, {}),
                work_style=work_styles.get(code, {}),
                work_activities=activities.get(code, {}),
                training=education.get(code, {}),
                job_zone=zones.get(code),
                task_terms=tuple(tasks.get(code, [])),
                related_occupation_ids=tuple(dict.fromkeys(f"onet:{item}" for item in related.get(code, []))),
                evidence_count=sum(len(values.get(code, {})) for values in evidence_sets) + len(tasks.get(code, [])) + len(related.get(code, [])),
                data_completeness=min(1.0, 0.15 + 0.09 * present + (0.10 if zones.get(code) else 0) + (0.08 if tasks.get(code) else 0) + (0.07 if related.get(code) else 0)),
                provenance=("O*NET", f"O*NET:{version}"),
            )
        )
    return records
