from __future__ import annotations

import csv
import io
import zipfile
from collections import defaultdict
from pathlib import Path

from orientation.occupation_knowledge.models import OccupationRecord


def _rows(archive: zipfile.ZipFile, filename: str) -> list[dict[str, str]]:
    name = next((item for item in archive.namelist() if item.casefold().endswith(filename.casefold())), None)
    if name is None:
        return []
    with archive.open(name) as raw:
        return list(csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig"), delimiter="\t"))


def _value(row: dict[str, str]) -> float | None:
    try:
        value = float(row.get("Data Value", "").strip())
    except ValueError:
        return None
    denominator = 100.0 if value > 7.0 else 7.0
    return max(0.0, min(1.0, value / denominator))


def _aggregate(rows: list[dict[str, str]], key_name: str = "Element Name") -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = defaultdict(dict)
    for row in rows:
        code = row.get("O*NET-SOC Code", "").strip()
        key = row.get(key_name, "").strip()
        value = _value(row)
        if code and key and value is not None:
            result[code][key] = max(result[code].get(key, 0.0), value)
    return result


def read_onet_zip(path: Path, version: str = "31.0") -> list[OccupationRecord]:
    """Read the official O*NET 31.0 tabular archive and enrich occupation profiles."""
    if version != "31.0":
        raise ValueError(f"unsupported_onet_version:{version}")
    with zipfile.ZipFile(path) as archive:
        occupations = _rows(archive, "Occupation Data.txt")
        abilities = _aggregate(_rows(archive, "Abilities.txt"))
        skills = _aggregate(_rows(archive, "Skills.txt"))
        knowledge = _aggregate(_rows(archive, "Knowledge.txt"))
        work_styles = _aggregate(_rows(archive, "Work Styles.txt"))
        activities = _aggregate(_rows(archive, "Work Activities.txt"))
        related_rows = _rows(archive, "Related Occupations.txt")
        job_zones = _rows(archive, "Job Zones.txt")
        interests = _rows(archive, "Interests.txt")
        essential_skills = _aggregate(_rows(archive, "Essential Skills.txt"))
        transferable_skills = _aggregate(_rows(archive, "Transferable Skills.txt"))
        training = _aggregate(_rows(archive, "Training and Experience.txt"))
        task_rows = _rows(archive, "Task Statements.txt")

    riasec: dict[str, dict[str, float]] = defaultdict(dict)
    for row in interests:
        code = row.get("O*NET-SOC Code", "").strip()
        name = row.get("Element Name", "").strip().casefold()
        value = _value(row)
        if not code or value is None:
            continue
        for key in ("realistic", "investigative", "artistic", "social", "enterprising", "conventional"):
            if key in name:
                riasec[code][key] = value

    related: dict[str, list[str]] = defaultdict(list)
    for row in related_rows:
        code = row.get("O*NET-SOC Code", "").strip()
        related_code = row.get("Related O*NET-SOC Code", "").strip()
        if code and related_code:
            related[code].append(f"onet:{related_code}")

    zones = {
        row.get("O*NET-SOC Code", "").strip(): int(row["Job Zone"])
        for row in job_zones
        if row.get("O*NET-SOC Code", "").strip() and row.get("Job Zone", "").isdigit()
    }
    tasks: dict[str, list[str]] = defaultdict(list)
    for row in task_rows:
        code = row.get("O*NET-SOC Code", "").strip()
        task = row.get("Task", "").strip()
        if code and task and len(tasks[code]) < 12:
            tasks[code].append(task)

    records: list[OccupationRecord] = []
    for row in occupations:
        code = row.get("O*NET-SOC Code", "").strip()
        title = row.get("Title", "").strip()
        if not code or not title:
            continue
        skill_map = {**transferable_skills.get(code, {}), **essential_skills.get(code, {}), **skills.get(code, {})}
        records.append(
            OccupationRecord(
                occupation_id=f"onet:{code}",
                source="onet",
                source_version=version,
                title=title,
                description=row.get("Description", "").strip(),
                onet_soc_code=code,
                riasec=riasec.get(code, {}),
                abilities=abilities.get(code, {}),
                skills=skill_map,
                knowledge=knowledge.get(code, {}),
                work_style=work_styles.get(code, {}),
                work_activities=activities.get(code, {}),
                job_zone=zones.get(code),
                training=training.get(code, {}),
                task_terms=tuple(tasks.get(code, [])),
                related_occupation_ids=tuple(dict.fromkeys(related.get(code, []))),
                evidence_count=sum(bool(item.get(code)) for item in (abilities, skills, knowledge, work_styles, activities, training)) + len(related.get(code, [])) + len(tasks.get(code, [])),
                data_completeness=min(1.0, 0.15 + 0.08 * sum(bool(item.get(code)) for item in (abilities, skills, knowledge, work_styles, activities, training)) + (0.15 if zones.get(code) else 0.0) + (0.10 if tasks.get(code) else 0.0)),
            )
        )
    return records
