from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeSource:
    name: str
    version: str
    authority: str
    landing_url: str
    purpose: str


SOURCES = (
    KnowledgeSource(
        "ESCO",
        "1.2.1",
        "European Commission",
        "https://esco.ec.europa.eu/en/use-esco/download",
        "Multilingual occupations, skills, competences and occupation-skill relations.",
    ),
    KnowledgeSource(
        "ISCO-08",
        "2008",
        "International Labour Organization",
        "https://isco.ilo.org/en/isco-08/",
        "International hierarchical backbone covering jobs worldwide.",
    ),
    KnowledgeSource(
        "O*NET",
        "31.0",
        "U.S. Department of Labor / National Center for O*NET Development",
        "https://www.onetcenter.org/database.html",
        "Occupation descriptions plus skills, abilities, interests, work styles, tasks and work context.",
    ),
)


def source_manifest() -> tuple[KnowledgeSource, ...]:
    return SOURCES
