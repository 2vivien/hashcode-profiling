from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from collections.abc import Iterable

from orientation.occupation_knowledge.models import OccupationRecord


def _float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def _rows(path: Path | None) -> Iterable[dict[str, str]]:
    if path is None or not path.is_file():
        return ()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return tuple(csv.DictReader(handle))


def _normalize_rating(value: float) -> float:
    return max(0.0, min(1.0, value / 7.0))


RIASEC_NAMES = {
    "realistic": "realistic",
    "investigative": "investigative",
    "artistic": "artistic",
    "social": "social",
    "enterprising": "enterprising",
    "conventional": "conventional",
}

ABILITY_MAP = {
    "Oral Comprehension": "verbal",
    "Written Comprehension": "verbal",
    "Oral Expression": "verbal",
    "Written Expression": "verbal",
    "Mathematical Reasoning": "numerical",
    "Number Facility": "numerical",
    "Problem Sensitivity": "problem_solving",
    "Deductive Reasoning": "logical",
    "Inductive Reasoning": "logical",
    "Information Ordering": "logical",
    "Flexibility of Closure": "problem_solving",
    "Perceptual Speed": "problem_solving",
}

SKILL_MAP = {
    "Reading Comprehension": "verbal",
    "Writing": "verbal",
    "Speaking": "communication",
    "Active Listening": "communication",
    "Critical Thinking": "logical",
    "Mathematics": "numerical",
    "Active Learning": "technical_learning",
    "Learning Strategies": "technical_learning",
    "Monitoring": "problem_solving",
}

WORK_STYLE_MAP = {
    "Persistence": "persistence",
    "Initiative": "initiative",
    "Cooperation": "teamwork",
    "Social Orientation": "teamwork",
    "Independence": "autonomy",
    "Attention to Detail": "structure_preference",
    "Dependability": "structure_preference",
    "Adaptability/Flexibility": "adaptability",
    "Stress Tolerance": "uncertainty_tolerance",
}


def enrich_onet_records(
    records: list[OccupationRecord],
    career_interest_types: Path | None = None,
    abilities: Path | None = None,
    essential_skills: Path | None = None,
    work_styles: Path | None = None,
) -> list[OccupationRecord]:
    riasec: dict[str, dict[str, float]] = defaultdict(dict)
    ability_values: dict[str, dict[str, float]] = defaultdict(dict)
    skill_values: dict[str, dict[str, float]] = defaultdict(dict)
    work_style_values: dict[str, dict[str, float]] = defaultdict(dict)
    evidence: dict[str, int] = defaultdict(int)

    for row in _rows(career_interest_types):
        code = row.get("O*NET-SOC Code", "").strip()
        name = row.get("Element Name", "").strip().casefold()
        value = _float(row.get("Data Value", ""))
        if code and value is not None and row.get("Scale ID") == "OI" and name in RIASEC_NAMES:
            riasec[code][RIASEC_NAMES[name]] = _normalize_rating(value)
            evidence[code] += 1

    for row in _rows(abilities):
        code = row.get("O*NET-SOC Code", "").strip()
        name = row.get("Element Name", "").strip()
        key = ABILITY_MAP.get(name)
        value = _float(row.get("Data Value", ""))
        if code and key and value is not None:
            ability_values[code][key] = max(ability_values[code].get(key, 0.0), _normalize_rating(value))
            evidence[code] += 1

    for row in _rows(essential_skills):
        code = row.get("O*NET-SOC Code", "").strip()
        name = row.get("Element Name", "").strip()
        key = SKILL_MAP.get(name)
        value = _float(row.get("Data Value", ""))
        if code and key and value is not None:
            skill_values[code][key] = max(skill_values[code].get(key, 0.0), _normalize_rating(value))
            evidence[code] += 1

    for row in _rows(work_styles):
        code = row.get("O*NET-SOC Code", "").strip()
        name = row.get("Element Name", "").strip()
        key = WORK_STYLE_MAP.get(name)
        value = _float(row.get("Data Value", ""))
        if code and key and value is not None:
            work_style_values[code][key] = max(
                work_style_values[code].get(key, 0.0), _normalize_rating(value)
            )
            evidence[code] += 1

    enriched: list[OccupationRecord] = []
    for record in records:
        if not record.occupation_id.startswith("onet:"):
            enriched.append(record)
            continue
        code = record.occupation_id.removeprefix("onet:")
        count = evidence[code]
        completeness = min(1.0, 0.25 + count / 20.0)
        enriched.append(
            record.model_copy(
                update={
                    "riasec": riasec[code],
                    "abilities": ability_values[code],
                    "skills": skill_values[code],
                    "work_style": work_style_values[code],
                    "evidence_count": record.evidence_count + count,
                    "data_completeness": completeness,
                }
            )
        )
    return enriched
