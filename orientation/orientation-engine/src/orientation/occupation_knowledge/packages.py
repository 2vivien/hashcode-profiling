from __future__ import annotations

import csv
import io
import zipfile
from collections import defaultdict
from pathlib import Path

from orientation.occupation_knowledge.models import OccupationRecord
from orientation.occupation_knowledge.taxonomy import major_group


def _csv_from_zip(archive: zipfile.ZipFile, suffix: str, *, delimiter: str = ",") -> list[dict[str, str]]:
    names = [name for name in archive.namelist() if name.lower().endswith(suffix.lower())]
    if not names:
        return []
    with archive.open(names[0]) as raw:
        return list(csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig"), delimiter=delimiter))


def read_esco_zip(path: Path, version: str = "v1.2.1", language: str = "en") -> list[OccupationRecord]:
    """Read ESCO occupations and preserve essential/optional skill relations."""
    if version != "v1.2.1":
        raise ValueError(f"unsupported_esco_version:{version}")
    with zipfile.ZipFile(path) as archive:
        occupations = _csv_from_zip(archive, f"occupations_{language}.csv")
        relations = _csv_from_zip(archive, "occupationSkillRelations.csv")
        skills = _csv_from_zip(archive, f"skills_{language}.csv")

    skill_titles = {
        row.get("conceptUri", "").strip(): row.get("preferredLabel", "").strip()
        for row in skills
        if row.get("conceptUri") and row.get("preferredLabel")
    }
    skill_ids: dict[str, set[str]] = defaultdict(set)
    essential: dict[str, set[str]] = defaultdict(set)
    optional: dict[str, set[str]] = defaultdict(set)
    for row in relations:
        occupation_uri = row.get("occupationUri", "").strip()
        skill_uri = row.get("skillUri", "").strip()
        relation_type = row.get("relationType", "").strip().casefold()
        if not occupation_uri or not skill_uri:
            continue
        skill_ids[occupation_uri].add(skill_uri)
        if relation_type == "essential":
            essential[occupation_uri].add(skill_uri)
        elif relation_type == "optional":
            optional[occupation_uri].add(skill_uri)

    records: list[OccupationRecord] = []
    for row in occupations:
        uri = row.get("conceptUri", "").strip()
        title = row.get("preferredLabel", "").strip()
        if not uri or not title:
            continue
        code = row.get("iscoGroup", "").strip() or row.get("iscoCode", "").strip()
        group = major_group(code)
        skills_for_occupation = tuple(sorted(skill_ids.get(uri, set())))
        records.append(
            OccupationRecord(
                occupation_id=f"esco:{uri}",
                source="esco",
                source_version=version,
                title=title,
                description=row.get("description", "").strip(),
                aliases=tuple(value.strip() for value in row.get("altLabels", "").split("|") if value.strip()),
                esco_uri=uri,
                isco08_code=code or None,
                isco_major_group=group.code if group else None,
                domains=(group.name_fr,) if group else (),
                skill_ids=skills_for_occupation,
                skill_labels={skill_id: skill_titles[skill_id] for skill_id in skills_for_occupation if skill_id in skill_titles},
                essential_skill_ids=tuple(sorted(essential.get(uri, set()))),
                optional_skill_ids=tuple(sorted(optional.get(uri, set()))),
                evidence_count=len(skills_for_occupation),
                data_completeness=min(1.0, 0.40 + len(skills_for_occupation) / 24.0),
            )
        )
    return records
