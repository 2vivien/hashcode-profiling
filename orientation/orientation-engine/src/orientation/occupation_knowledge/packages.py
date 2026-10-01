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


def _relation_kind(value: str) -> str:
    normalized = value.casefold().strip()
    if normalized.endswith("essential") or normalized == "essential":
        return "essential"
    if normalized.endswith("optional") or normalized == "optional":
        return "optional"
    return "unknown"


def read_esco_zip(path: Path, version: str = "v1.2.1", language: str = "en") -> list[OccupationRecord]:
    with zipfile.ZipFile(path) as archive:
        occupations = _csv_from_zip(archive, f"occupations_{language}.csv")
        relations = _csv_from_zip(archive, "occupationSkillRelations.csv")
        broader = _csv_from_zip(archive, "broaderRelationsOccPillar.csv")
        skills = _csv_from_zip(archive, f"skills_{language}.csv")

    skill_titles = {
        row.get("conceptUri", "").strip(): row.get("preferredLabel", "").strip()
        for row in skills
        if row.get("conceptUri") and row.get("preferredLabel")
    }
    broader_map: dict[str, list[str]] = defaultdict(list)
    for row in broader:
        child = (row.get("conceptUri") or row.get("childUri") or row.get("occupationUri") or "").strip()
        parent = (row.get("broaderUri") or row.get("parentUri") or "").strip()
        if child and parent:
            broader_map[child].append(parent)

    all_skills: dict[str, list[str]] = defaultdict(list)
    essential: dict[str, list[str]] = defaultdict(list)
    optional: dict[str, list[str]] = defaultdict(list)
    for row in relations:
        occupation_uri = row.get("occupationUri", "").strip()
        skill_uri = row.get("skillUri", "").strip()
        if not occupation_uri or not skill_uri:
            continue
        if skill_uri in skill_titles:
            all_skills[occupation_uri].append(skill_uri)
            kind = _relation_kind(row.get("relationType", ""))
            if kind == "essential":
                essential[occupation_uri].append(skill_uri)
            elif kind == "optional":
                optional[occupation_uri].append(skill_uri)

    records: list[OccupationRecord] = []
    for row in occupations:
        uri = row.get("conceptUri", "").strip()
        title = row.get("preferredLabel", "").strip()
        if not uri or not title:
            continue
        code = row.get("iscoGroup", "").strip() or row.get("iscoCode", "").strip()
        group = major_group(code)
        skill_ids = tuple(dict.fromkeys(all_skills.get(uri, [])))
        essential_ids = tuple(dict.fromkeys(essential.get(uri, [])))
        optional_ids = tuple(dict.fromkeys(optional.get(uri, [])))
        records.append(
            OccupationRecord(
                occupation_id=f"esco:{uri}",
                source="esco",
                source_version=version,
                title=title,
                description=row.get("description", "").strip(),
                aliases=tuple(value.strip() for value in row.get("altLabels", "").split("|") if value.strip()),
                isco08_code=code or None,
                isco_major_group=group.code if group else None,
                domains=(group.name_fr,) if group else (),
                esco_uri=uri,
                skill_ids=skill_ids,
                skill_labels={skill_id: skill_titles[skill_id] for skill_id in skill_ids},
                essential_skill_ids=essential_ids,
                optional_skill_ids=optional_ids,
                evidence_count=len(skill_ids),
                data_completeness=min(1.0, 0.30 + len(skill_ids) / 40.0),
                provenance=("ESCO", f"ESCO:{version}", f"ESCO:{language}"),
            )
        )
    return records
