from __future__ import annotations

import csv
import io
import zipfile
from collections import defaultdict
from pathlib import Path

from orientation.occupation_knowledge.models import OccupationRecord
from orientation.occupation_knowledge.taxonomy import major_group


def _csv_from_zip(archive: zipfile.ZipFile, suffix: str) -> list[dict[str, str]]:
    names = [name for name in archive.namelist() if name.lower().endswith(suffix.lower())]
    if not names:
        return []
    with archive.open(names[0]) as raw:
        return list(csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig")))


def read_esco_zip(path: Path, version: str = "v1.2.1", language: str = "en") -> list[OccupationRecord]:
    """Read an official ESCO language package without committing upstream data."""
    with zipfile.ZipFile(path) as archive:
        occupations = _csv_from_zip(archive, f"occupations_{language}.csv")
        relations = _csv_from_zip(archive, "occupationSkillRelations.csv")
        skills = _csv_from_zip(archive, f"skills_{language}.csv")

    skill_titles = {
        row.get("conceptUri", "").strip(): row.get("preferredLabel", "").strip()
        for row in skills
        if row.get("conceptUri") and row.get("preferredLabel")
    }
    related: dict[str, list[str]] = defaultdict(list)
    for row in relations:
        occupation_uri = row.get("occupationUri", "").strip()
        skill_uri = row.get("skillUri", "").strip()
        if occupation_uri and skill_uri and skill_titles.get(skill_uri):
            related[occupation_uri].append(skill_titles[skill_uri])

    records: list[OccupationRecord] = []
    for row in occupations:
        uri = row.get("conceptUri", "").strip()
        title = row.get("preferredLabel", "").strip()
        if not uri or not title:
            continue
        code = row.get("iscoGroup", "").strip() or row.get("iscoCode", "").strip()
        group = major_group(code)
        skills_for_occupation = tuple(sorted(set(related.get(uri, []))))
        records.append(
            OccupationRecord(
                occupation_id=f"esco:{uri}",
                source="esco",
                source_version=version,
                title=title,
                description=row.get("description", "").strip(),
                aliases=tuple(
                    value.strip()
                    for value in row.get("altLabels", "").split("|")
                    if value.strip()
                ),
                isco08_code=code or None,
                isco_major_group=group.code if group else None,
                domains=(group.name_fr,) if group else (),
                skill_ids=skills_for_occupation,
                evidence_count=len(skills_for_occupation),
                data_completeness=min(1.0, 0.35 + len(skills_for_occupation) / 20.0),
            )
        )
    return records


def read_onet_zip(path: Path, version: str = "31.0") -> list[OccupationRecord]:
    """Read the official O*NET tabular archive without committing upstream data."""
    with zipfile.ZipFile(path) as archive:
        rows = _csv_from_zip(archive, "Occupation Data.txt")
        if not rows:
            rows = _csv_from_zip(archive, "Occupation Data.csv")

    records: list[OccupationRecord] = []
    for row in rows:
        code = row.get("O*NET-SOC Code", "").strip()
        title = row.get("Title", "").strip()
        if not code or not title:
            continue
        records.append(
            OccupationRecord(
                occupation_id=f"onet:{code}",
                source="onet",
                source_version=version,
                title=title,
                description=row.get("Description", "").strip(),
                evidence_count=1,
                data_completeness=0.25,
            )
        )
    return records
