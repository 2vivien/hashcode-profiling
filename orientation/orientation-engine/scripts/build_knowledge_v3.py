#!/usr/bin/env python3
"""Construit la connaissance v3 : les fiches métiers réelles du ROME.

v2 portait 24 occupations **curées à la main**. v3 y ajoute les **1 911 fiches
métiers du ROME** (France Travail, open data juin 2026) : nomenclature
officielle française, en français, donc utilisable telle quelle.

Ce que v3 ne fait PAS, et qu'il faut assumer :

- **les fiches ROME ne sont rattachées aux directions que par appariement
  textuel** (`relation: "matched"`, poids = confiance). Le reste du catalogue
  est conservé mais non apparié : mieux vaut une donnée orpheline qu'un
  faux positif dans le scoring.
- **la répartition de genre n'existe pas dans l'open data ROME.** Le fichier
  de tags ne contient que 10 colonnes (domaines, transitions, cadre,
  réglementé). `gender` est donc déduit de la convention d'écriture
  inclusive du ROME ("Conducteur / Conductrice"), et `gender_distribution`
  reste vide tant qu'aucune source réelle n'a été identifiée.
- les competences ROME (19 480) sont exportées à part dans `competences.json` :
  elles ne doivent pas contaminer `skills.json`, qui est le vocabulaire de
  scoring du moteur.

Usage : python3 scripts/build_knowledge_v3.py
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import warnings
from pathlib import Path
from typing import Any

import openpyxl

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

ROOT = Path(__file__).resolve().parents[1] / "data" / "knowledge"
SRC = ROOT / "v2"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "rome"
DST = ROOT / "v3"

VERSION = "v3"
ROME_RELEASE = "2026-06"

# Fiches métier : le fichier de tags porte le libellé et les marqueurs
# (transitions, emploi cadre, emploi réglementé) de chaque fiche.
TAGS_FILE = "250528-fiches-rome-26m06-tag-pour-diffusion.xlsx"
TAGS_SHEET = "Tag des fiches ROME"
# Arborescence des compétences : 19 480 lignes en feuille « Données brutes Comp. »
COMPETENCES_FILE = "rome-arborescence-des-competences-juin-2026.xlsx"

STOPWORDS = {"de", "du", "des", "le", "la", "les", "et", "en", "d", "a", "au", "aux"}
# Mots trop génériques pour porter un appariement fiable.
GENERIC = {"ingenieur", "technicien", "cadre", "employe", "agent", "responsable", "specialiste", "consultant"}
# Mots *polysémiques* : « sécurité » peut désigner la cybersécurité comme la sécurité
# sociale, « service » l Pyramide de partout. Les exiger rendrait l'appariement faux.
AMBIGUOUS = {
    "securite",
    "social",
    "sociale",
    "service",
    "performance",
    "systeme",
    "administratif",
    "commercial",
    "industriel",
    "integre",
    "production",
    "gestion",
    "technique",
    "expert",
    "controle",
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    return "".join(char for char in text if not unicodedata.combining(char)).lower()


def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9+]{3,}", normalize(text))
    return {word for word in words if word not in STOPWORDS}


def stem(word: str) -> str:
    """Rapproche les variantes du pluriel français.

    Règle -eau / -eaux (réseau → réseaux, bateau → bateaux), puis -s simple.
    """
    if len(word) > 4 and word.endswith("eaux"):
        return word[:-3]
    if len(word) > 3 and word.endswith("eau"):
        return word[:-2]
    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def match_direction(label: str, domaine: str, seeds: dict[str, set[str]]) -> tuple[str, float] | None:
    """Appariement lexical à **haute précision**.

    On n'accepte que des correspondances qui ne puissent pas venir d'une
    homonymie : le mot partagé doit être absent du registre des mots
    polysémiques, et il faut soit plusieurs mots distinctifs, soit une amorce
    réduite à un seul mot vraiment spécifique. En dessous, la fiche reste dans
    le catalogue mais orpheline : mieux vaut une donnée non appariée qu'un
    faux positif dans le scoring.
    """
    haystack = {stem(token) for token in tokens(label) | tokens(domaine)}
    best: tuple[str, float] | None = None
    for direction_id, raw_seeds in seeds.items():
        # Les amorces sont normalisées comme le texte recherché : sans cela,
        # « réseau » (amorce) ne rencontrerait jamais « réseaux » (fiche).
        seed_tokens = {stem(token) for token in raw_seeds}
        distinctive = {token for token in haystack & seed_tokens} - AMBIGUOUS
        if not distinctive:
            continue
        if len(distinctive) >= 2:
            score = len(distinctive) / max(1, len(seed_tokens))
        elif len(seed_tokens) == 1:
            score = 0.9
        else:
            # Un seul mot partagé alors que l'amorce en contient plusieurs : trop faible.
            continue
        if score >= 0.9 and (best is None or score > best[1]):
            best = (direction_id, round(min(1.0, score), 3))
    return best


def read_rome_tags(path: Path) -> list[dict[str, Any]]:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook[TAGS_SHEET]
    rows = sheet.iter_rows(values_only=True)
    header = [str(cell).strip() if cell is not None else "" for cell in next(rows)]
    records: list[dict[str, Any]] = []
    for row in rows:
        if not row or row[0] is None:
            continue
        entry = dict(zip(header, row, strict=False))
        code = str(entry.get("Code ROME") or "").strip()
        label = str(entry.get("Libellé fiche ROME") or "").strip()
        if not code or not label:
            continue
        records.append(
            {
                "code": code,
                "label": label,
                "grand_domaine": str(entry.get("Grand domaine") or "").strip(),
                "domaine": str(entry.get("Domaine") or "").strip(),
                "code_ogr": str(entry.get("Code OGR") or "").strip() or None,
                "transition_ecologique": entry.get("Transition Ecologique"),
                "transition_numerique": entry.get("Transition Numérique"),
                "transition_demographique": entry.get("Transition Démographique"),
                "emploi_cadre": entry.get("Emploi cadre ?"),
                "emploi_reglemente": entry.get("Emploi réglementé ?"),
            }
        )
    workbook.close()
    return records


def read_rome_competences(path: Path) -> list[dict[str, Any]]:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook["Données brutes Comp."]
    rows = sheet.iter_rows(values_only=True)
    header = [str(cell).strip() if cell is not None else "" for cell in next(rows)]

    def value(entry: dict[str, Any], name: str) -> str:
        for key, cell in zip(header, entry, strict=False):
            if key == name:
                return str(cell).strip() if cell is not None else ""
        return ""

    records: list[dict[str, Any]] = []
    for row in rows:
        if not row or row[0] is None:
            continue
        entry = dict(zip(header, row, strict=False))
        label = value(entry, "5 - Compétence")
        if not label:
            continue
        records.append(
            {
                "competence_id": value(entry, "0 - Code domaine compétence"),
                "domaine": value(entry, "1 - Domaine compétence"),
                "enjeu": value(entry, "2 - Enjeu"),
                "objectif": value(entry, "3 - Objectif"),
                "macro_competence": value(entry, "4 - Macro-compétence"),
                "label": label,
            }
        )
    workbook.close()
    return records


def derive_gender(label: str) -> str:
    """Le ROME écrit les métiers en paire inclusive (« X / Y »).

    C'est une convention d'écriture, pas une statistique de terrain : on ne
    prétend donc rien déduire de la répartition réelle des personnes.
    """
    parts = [part.strip() for part in label.split("/")]
    return "mixed" if len(parts) > 1 and all(parts) else "unknown"


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)

    directions = json.loads((SRC / "directions.json").read_text(encoding="utf-8"))
    curated = json.loads((SRC / "occupations.json").read_text(encoding="utf-8"))
    formations = json.loads((SRC / "formations.json").read_text(encoding="utf-8"))

    rome = read_rome_tags(RAW / TAGS_FILE)
    competences = read_rome_competences(RAW / COMPETENCES_FILE)

    # Amorces d'appariement : les titres curés de v2, dont on ne garde que les
    # mots distinctifs (ceux qui ne sont pas des mots métier génériques).
    seeds: dict[str, set[str]] = {}
    for occupation in curated:
        seed = {token for token in tokens(occupation["title"]) if token not in GENERIC}
        if not seed:
            seed = tokens(occupation["title"])
        # Les ids curés sont de la forme "<direction_id>-<suffixe>".
        direction_id = occupation["occupation_id"].rsplit("-", 1)[0]
        if seed and direction_id not in seeds:
            seeds[direction_id] = seed

    occupations: list[dict[str, Any]] = []
    matched = 0
    for entry in rome:
        direction = match_direction(entry["label"], entry["domaine"], seeds)
        if direction is not None:
            matched += 1
        occupations.append(
            {
                "occupation_id": f"rome-{entry['code'].lower()}",
                "source": "rome",
                "source_version": ROME_RELEASE,
                "title": entry["label"],
                "description": f"Fiche métier ROME {entry['code']} — {entry['domaine']}",
                "aliases": [],
                "grand_domaine": entry["grand_domaine"],
                "domaine": entry["domaine"],
                "code_ogr": entry["code_ogr"],
                "isco08_code": None,
                "language": "fr",
                "original_title": None,
                "translation_status": "source",
                "gender": derive_gender(entry["label"]),
                "gender_distribution": {},
                "tags": {
                    "transition_ecologique": entry["transition_ecologique"],
                    "transition_numerique": entry["transition_numerique"],
                    "transition_demographique": entry["transition_demographique"],
                    "emploi_cadre": entry["emploi_cadre"],
                    "emploi_reglemente": entry["emploi_reglemente"],
                },
                "matched_direction": direction[0] if direction else None,
                "match_confidence": direction[1] if direction else None,
                "evidence_count": 3,
                "data_completeness": 0.4,
            }
        )

    # Les occupations curées restent : elles portent les dimensions de scoring
    # (riasec, abilities, skills...) que le ROME ne fournit pas.
    for occupation in curated:
        enriched = dict(occupation)
        enriched.setdefault("language", "fr")
        enriched.setdefault("original_title", None)
        enriched.setdefault("translation_status", "source")
        enriched.setdefault("gender", "unknown")
        enriched.setdefault("gender_distribution", {})
        occupations.append(enriched)

    mappings: list[dict[str, Any]] = json.loads((SRC / "mappings.json").read_text(encoding="utf-8"))
    for occupation in occupations:
        direction_id = occupation.get("matched_direction")
        if not direction_id:
            continue
        mappings.append(
            {
                "id": f"{direction_id}->{occupation['occupation_id']}",
                "source_id": direction_id,
                "target_id": occupation["occupation_id"],
                "relation": "matched",
                "weight": occupation.get("match_confidence") or 0.5,
                "data": {"method": "lexical", "rome_release": ROME_RELEASE},
            }
        )

    for direction in directions:
        direction["knowledge_version"] = VERSION
        direction["occupations"] = [item["occupation_id"] for item in occupations if item.get("matched_direction") == direction["direction_id"]] or direction.get("occupations", [])

    (DST / "directions.json").write_text(json.dumps(directions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DST / "occupations.json").write_text(json.dumps(occupations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DST / "competences.json").write_text(json.dumps(competences, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DST / "formations.json").write_text(json.dumps(formations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DST / "mappings.json").write_text(json.dumps(mappings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DST / "skills.json").write_text((SRC / "skills.json").read_text(encoding="utf-8"), encoding="utf-8")

    digest = hashlib.sha256((DST / "occupations.json").read_bytes()).hexdigest()
    manifest = {
        "version": VERSION,
        "source": (
            f"ROME {ROME_RELEASE} (France Travail, open data) — {len(rome)} fiches métiers "
            f"+ {len(competences)} compétences ; les {len(curated)} occupations curées de v2 sont conservées "
            "car elles portent les dimensions de scoring absentes du ROME"
        ),
        "date": "2026-10-10",
        "sha256": digest,
        "item_counts": {
            "directions": len(directions),
            "occupations": len(occupations),
            "occupations_rome": len(rome),
            "occupations_curated": len(curated),
            "occupations_matched": matched,
            "competences": len(competences),
            "formations": len(formations),
            "mappings": len(mappings),
            "skills": len(json.loads((SRC / "skills.json").read_text(encoding="utf-8"))),
        },
        "transformation_rules": [
            "identifiants ROME préfixés 'rome-' pour ne pas entrer en collision avec la curation",
            "appariement lexical conservateur (relation 'matched', poids = confiance)",
            "genre déduit de la paire inclusive du libellé, jamais d'une statistique",
            "competences.json est distinct de skills.json (vocabulaire de scoring)",
        ],
        "known_gaps": [
            "gender_distribution vide : aucune source de répartition par métier en open data",
            "formations encore curées (RNCP non ingéré)",
            "O*NET et ESCO non encore fusionnés : il manque le crosswalk officiel pour apparier",
        ],
    }
    (DST / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[v3] {manifest['item_counts']} sha256={digest[:12]}…")


if __name__ == "__main__":
    main()
