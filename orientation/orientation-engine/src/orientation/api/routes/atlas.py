"""Atlas : où sont les données, et comment sont-elles réparties.

Répond à deux questions qu'on se pose légitimement avant d'utiliser un moteur
d'orientation :

1. **« Ça couvre quoi, et où ? »** — le périmètre géographique, versionné avec
   la connaissance, plus la répartition des métiers par pays.
2. **« C'est réparti comment ? »** — les grands domaines d'activité et les
   domaines de compétences, avec les effectifs réels.

Toutes les valeurs viennent de la base ou du fichier de couverture. Rien n'est
écrit en dur : si la France est la seule nation couverte, la carte le montre.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from orientation.api.routes.recommendations import get_service
from orientation.config.settings import Settings, get_settings
from orientation.infrastructure.knowledge.coverage import coverage_for
from orientation.infrastructure.knowledge.repository import KnowledgeRepository

router = APIRouter(tags=["atlas"])


# Découpage lisible d'un grand domaine ROME du type
# « K - Services à la personne et à la collectivité ».
def _split_domain(raw: str) -> tuple[str, str]:
    text = (raw or "").strip()
    if " - " in text:
        code, _, name = text.partition(" - ")
        return code.strip(), name.strip()
    return "", text


@router.get("/atlas")
def get_atlas(
    limit: int = Query(default=20, ge=1, le=100),
    service: Any = Depends(get_service),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Répartition réelle des métiers et des compétences, plus le périmètre."""
    bundle = service.knowledge()
    repository = KnowledgeRepository(service.loader.repository.root)
    coverage = coverage_for(bundle.version)

    occupation_domains: dict[str, int] = {}
    occupation_countries: dict[str, int] = {}
    gender_breakdown: dict[str, int] = {}
    language_breakdown: dict[str, int] = {}

    for occupation in bundle.occupations:
        gender = occupation.gender or "unknown"
        gender_breakdown[gender] = gender_breakdown.get(gender, 0) + 1
        language = occupation.language or "fr"
        language_breakdown[language] = language_breakdown.get(language, 0) + 1

        # Les grands domaines et le pays vivent dans la donnée de la fiche.
        raw_domain = occupation.grand_domaine or ""
        _code, domain_name = _split_domain(raw_domain)
        if domain_name:
            occupation_domains[domain_name] = occupation_domains.get(domain_name, 0) + 1
        # Le pays vient du périmètre de la connaissance, pas de la fiche :
        # une fiche ROME est française par construction, on ne va pas le
        # redéclarer 1 911 fois.
        if coverage.countries:
            for code in coverage.countries:
                occupation_countries[code] = occupation_countries.get(code, 0) + 1

    competences = _competence_domains(bundle.version)

    return {
        "coverage": coverage.describe(),
        "totals": {
            "directions": len(bundle.directions),
            "occupations": len(bundle.occupations),
            "formations": len(bundle.formations),
            "competences": competences.get("total", 0),
        },
        "occupations_by_domain": [{"domain": name, "count": count} for name, count in sorted(occupation_domains.items(), key=lambda item: -item[1])[:limit]],
        "occupations_by_country": [{"country": code, "count": count} for code, count in sorted(occupation_countries.items(), key=lambda item: -item[1])],
        "occupations_by_gender": [{"gender": key, "count": value} for key, value in sorted(gender_breakdown.items(), key=lambda item: -item[1])],
        "occupations_by_language": [{"language": key, "count": value} for key, value in sorted(language_breakdown.items(), key=lambda item: -item[1])],
        "competences_by_domain": competences.get("domains", []),
        "repository": str(repository.root),
    }


def _competence_domains(version: str) -> dict[str, Any]:
    """Répartition des compétences par domaine, lue depuis le fichier vN."""
    import json
    from pathlib import Path

    root = Path("data/knowledge") / version / "competences.json"
    if not root.is_file():
        return {"total": 0, "domains": []}
    try:
        payload = json.loads(root.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"total": 0, "domains": []}

    counts: dict[str, int] = {}
    for competence in payload:
        domain = str(competence.get("domaine") or "").strip()
        if domain:
            counts[domain] = counts.get(domain, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: -item[1])
    return {
        "total": len(payload),
        "domains": [{"domain": name, "count": count} for name, count in ordered],
    }
