#!/usr/bin/env python3
"""Construit la connaissance v2 (directions enrichies + occupations + formations + mappings).

Provenance : les occupations et formations ci-dessous sont une **curation pédagogique
interne** dérivée des directions v1. Elles ne sont PAS de l'ESCO ni de l'O*NET :
`source: "curated"` est donc utilisé, et `evidence_count` reste bas pour ne pas
sur-vendre la qualité de la donnée.

Les exports réels ESCO/O*NET devront alimenter une version ultérieure (issue #21).

Usage : python3 scripts/build_knowledge_v2.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1] / "data" / "knowledge"
SRC = ROOT / "v1"
DST = ROOT / "v2"

VERSION = "v2"

# (suffixe, titre, code ISCO-08, groupe majeur, thème)
OCCUPATIONS: dict[str, list[tuple[str, str, str, str, str]]] = {
    "software-engineering": [
        ("dev", "Développeur logiciel", "2510", "2", "software"),
        ("architect", "Architecte logiciel", "2510", "2", "architecture"),
    ],
    "cybersecurity": [
        ("analyst", "Analyste sécurité", "2621", "2", "security"),
        ("engineer", "Ingénieur sécurité des systèmes", "2621", "2", "security"),
    ],
    "data-science": [
        ("scientist", "Data scientist", "2511", "2", "data"),
        ("analyst", "Analyste de données", "2511", "2", "data"),
    ],
    "network-engineering": [
        ("engineer", "Ingénieur réseaux", "2521", "2", "network"),
        ("technician", "Technicien d'exploitation réseau", "2523", "3", "network"),
    ],
    "ux-ui": [
        ("designer", "Designer d'expérience utilisateur", "2683", "2", "design"),
        ("researcher", "Chercheur UX", "2683", "2", "research"),
    ],
    "graphic-design": [
        ("designer", "Graphiste", "2681", "2", "design"),
        ("motion", "Graphiste motion / publicité", "2681", "2", "design"),
    ],
    "digital-marketing": [
        ("manager", "Responsable marketing digital", "2421", "1", "marketing"),
        ("specialist", "Spécialiste acquisition et référencement", "2431", "3", "marketing"),
    ],
    "teaching": [
        ("teacher", "Enseignant du secondaire", "2310", "3", "teaching"),
        ("trainer", "Formateur en entreprise", "2423", "3", "teaching"),
    ],
    "psychology": [
        ("psychologist", "Psychologue", "2442", "2", "psychology"),
        ("counselor", "Conseiller en orientation professionnelle", "2442", "2", "social"),
    ],
    "accounting": [
        ("accountant", "Comptable", "2411", "3", "accounting"),
        ("controller", "Contrôleur de gestion", "2411", "3", "analysis"),
    ],
    "medicine": [
        ("doctor", "Médecin", "2211", "2", "medicine"),
        ("nurse", "Infirmierritorial", "2211", "2", "care"),
    ],
    "law": [
        ("lawyer", "Avocat", "2421", "2", "law"),
        ("juriste", "Juriste en entreprise", "2421", "2", "law"),
    ],
}

# (suffixe, titre, niveau 0-1, durée en années, themes)
FORMATIONS: dict[str, list[tuple[str, str, float, int, str]]] = {
    "software-engineering": [
        ("licence-info", "Licence Informatique", 0.55, 3, "informatique"),
        ("master-info", "Master Informatique", 0.8, 5, "informatique"),
    ],
    "cybersecurity": [
        ("licence-info-sec", "Licence Informatique (sécurité)", 0.6, 3, "informatique"),
        ("master-sec", "Master Cybersécurité", 0.85, 5, "securite"),
    ],
    "data-science": [
        ("licence-math-info", "Licence Mathématiques-Informatique", 0.65, 3, "donnees"),
        ("master-data", "Master Data Science", 0.85, 5, "donnees"),
    ],
    "network-engineering": [
        ("licence-reseau", "Licence Réseaux et Télécommunications", 0.6, 3, "reseaux"),
        ("master-reseau", "Master Réseaux et Systèmes Distribués", 0.85, 5, "reseaux"),
    ],
    "ux-ui": [("licence-design", "Licence Design et Communication", 0.55, 3, "design")],
    "graphic-design": [
        ("licence-design-2", "Licence Design graphique", 0.55, 3, "design"),
        ("dsm", "École Supérieure des Arts Décoratifs (DN MADE)", 0.75, 3, "design"),
    ],
    "digital-marketing": [
        ("licence-mkt", "Licence Marketing et Communication", 0.55, 3, "marketing"),
        ("master-mkt", "Master Marketing Digital", 0.8, 5, "marketing"),
    ],
    "teaching": [("capes", "Capes / Master Éducation et Formation", 0.7, 5, "education")],
    "psychology": [("licence-psy", "Licence Psychologie", 0.65, 3, "psychologie")],
    "accounting": [
        (
            "licence-gestion",
            "Licence Gestion des entreprises et des administrations",
            0.55,
            3,
            "gestion",
        ),
        ("dcf", "Diplôme d'expert-comptable (DCG + DEC)", 0.9, 7, "gestion"),
    ],
    "medicine": [("doctorat-med", "Diplôme de Docteur en Médecine", 0.95, 9, "sante")],
    "law": [
        ("licence-droit", "Licence Droit", 0.65, 3, "droit"),
        ("master-droit", "Master Droit des affaires", 0.85, 5, "droit"),
    ],
}


def scale(values: dict[str, float], factor: float) -> dict[str, float]:
    return {key: round(min(1.0, max(0.0, value * factor)), 3) for key, value in values.items()}


def build_occupations(direction: dict[str, Any], taxonomy: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    prefix = direction["direction_id"]
    for suffix, title, isco, major, _theme in OCCUPATIONS[direction["direction_id"]]:
        records.append(
            {
                "occupation_id": f"{prefix}-{suffix}",
                "source": "curated",
                "source_version": "2026.1",
                "title": title,
                "description": (f"Curation interne dérivée de la direction « {direction['canonical_name']} » (taxonomie {taxonomy})."),
                "aliases": [],
                "isco08_code": isco,
                "isco_major_group": major,
                "domains": [taxonomy],
                "riasec": scale(direction.get("interests", {}), 1.0),
                "abilities": scale(direction.get("abilities", {}), 1.0),
                "skills": scale(direction.get("skills", {}), 1.0),
                "values": scale(direction.get("values", {}), 1.0),
                "work_style": {"autonomy": direction.get("values", {}).get("autonomy", 0.5)},
                "environment": scale(direction.get("values", {}), 0.8),
                "education_level": 0.6,
                "job_zone": int(major) if major.isdigit() else 4,
                "skill_ids": sorted(direction.get("skills", {}).keys()),
                "task_terms": [],
                "evidence_count": 1,
                "data_completeness": 0.55,
            }
        )
    return records


def build_formations(direction: dict[str, Any], taxonomy: str) -> list[dict[str, Any]]:
    prefix = direction["direction_id"]
    return [
        {
            "formation_id": f"{prefix}-{suffix}",
            "title": title,
            "level": level,
            "duration_years": duration,
            "fields": [taxonomy, theme],
            "domains": [taxonomy],
            "description": (f"Parcours issu de la curation de la direction « {direction['canonical_name']} »."),
            "knowledge_version": VERSION,
        }
        for suffix, title, level, duration, theme in FORMATIONS[direction["direction_id"]]
    ]


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    v1_directions = json.loads((SRC / "directions.json").read_text(encoding="utf-8"))

    directions: list[dict[str, Any]] = []
    occupations: list[dict[str, Any]] = []
    formations: list[dict[str, Any]] = []
    mappings: list[dict[str, Any]] = []

    for source in v1_directions:
        direction = dict(source)
        taxonomy = direction["taxonomy"]
        occ = build_occupations(direction, taxonomy)
        forms = build_formations(direction, taxonomy)
        direction["occupations"] = [item["occupation_id"] for item in occ]
        direction["formations"] = [item["formation_id"] for item in forms]
        direction["knowledge_version"] = VERSION
        directions.append(direction)
        occupations.extend(occ)
        formations.extend(forms)
        mappings.extend(
            {
                "id": f"{direction['direction_id']}->{item['occupation_id']}",
                "source_id": direction["direction_id"],
                "target_id": item["occupation_id"],
                "relation": "offers_occupation",
                "weight": 1.0,
            }
            for item in occ
        )
        mappings.extend(
            {
                "id": f"{direction['direction_id']}->{item['formation_id']}",
                "source_id": direction["direction_id"],
                "target_id": item["formation_id"],
                "relation": "offers_formation",
                "weight": 1.0,
            }
            for item in forms
        )

    (DST / "directions.json").write_text(json.dumps(directions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DST / "occupations.json").write_text(json.dumps(occupations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DST / "formations.json").write_text(json.dumps(formations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DST / "mappings.json").write_text(json.dumps(mappings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DST / "skills.json").write_text((SRC / "skills.json").read_text(encoding="utf-8"), encoding="utf-8")

    digest = hashlib.sha256((DST / "directions.json").read_bytes()).hexdigest()
    manifest = {
        "version": VERSION,
        "source": ("Otheloo V2 curated catalog (interne) — occupations et formations dérivées des directions v1"),
        "date": "2026-10-10",
        "directions": len(directions),
        "sha256": digest,
        "item_counts": {
            "directions": len(directions),
            "occupations": len(occupations),
            "formations": len(formations),
            "mappings": len(mappings),
            "skills": len(json.loads((SRC / "skills.json").read_text(encoding="utf-8"))),
        },
        "transformation_rules": [
            "canonical IDs",
            "normalized dimensions in [0,1]",
            "unknown data is not zero",
            "occupations/formations: curation interne, PAS ESCO/O*NET",
        ],
    }
    (DST / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[v2] {manifest['item_counts']} sha256={digest[:12]}…")


if __name__ == "__main__":
    main()
