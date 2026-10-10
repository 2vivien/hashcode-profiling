"""Découpage de la connaissance en documents retrievables.

La connaissance est faite d'objets structurés (directions, fiches métier,
compétences, formations). Un système de récupération parle en *documents* :
on construit donc un index parallèle, sans toucher aux objets métier, et chaque
document garde sa provenance (source, version, langue) pour que l'explication
puisse remonter jusqu'à la donnée d'origine.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import Any

DOC_KINDS = ("direction", "occupation", "competence", "formation")


def normalize(text: str) -> str:
    """Minuscules sans accents : l'index lexical doit ignorer les diacritiques."""
    decomposed = unicodedata.normalize("NFKD", text or "")
    return "".join(char for char in decomposed if not unicodedata.combining(char)).lower()


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9+#]{2,}", normalize(text))


@dataclass(frozen=True)
class Document:
    """Un fragment retrievable, toujours rattaché à sa source."""

    doc_id: str
    kind: str
    title: str
    body: str
    source: str
    source_version: str
    language: str = "fr"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def text(self) -> str:
        return f"{self.title}\n{self.body}".strip()

    def provenance(self) -> str:
        return f"{self.kind}:{self.doc_id}@{self.source_version}"


@dataclass(frozen=True)
class DocumentBatch:
    documents: list[Document]

    def __len__(self) -> int:
        return len(self.documents)


def _occupation_documents(occupations: Iterable[Any], version: str) -> Iterator[Document]:
    for occupation in occupations:
        raw = getattr(occupation, "data", None) or {}
        tags = raw.get("tags") or {}
        marker = " · ".join(f"{key}={value}" for key, value in tags.items() if value not in (None, "", "Non"))
        body = " ".join(
            part
            for part in (
                str(raw.get("description") or ""),
                str(raw.get("domaine") or ""),
                str(raw.get("grand_domaine") or ""),
                marker,
                " ".join(str(item) for item in (raw.get("aliases") or [])),
            )
            if part
        )
        yield Document(
            doc_id=getattr(occupation, "occupation_id", ""),
            kind="occupation",
            title=getattr(occupation, "title", "") or "",
            body=body,
            source=getattr(occupation, "source", "") or "unknown",
            source_version=str(raw.get("source_version") or version),
            metadata={
                "isco08": raw.get("isco08_code"),
                "gender": raw.get("gender"),
                "matched_direction": raw.get("matched_direction"),
            },
        )


def _formation_documents(formations: Iterable[Any], version: str) -> Iterator[Document]:
    for formation in formations:
        raw = getattr(formation, "data", None) or {}
        body = " ".join(
            part
            for part in (
                str(raw.get("description") or ""),
                " ".join(str(item) for item in (raw.get("fields") or [])),
                f"durée {raw.get('duration_years')} ans" if raw.get("duration_years") else "",
            )
            if part
        )
        yield Document(
            doc_id=getattr(formation, "formation_id", ""),
            kind="formation",
            title=getattr(formation, "title", "") or "",
            body=body,
            source="curated",
            source_version=version,
            metadata={"level": raw.get("level"), "cefr": raw.get("cefr_level")},
        )


def _direction_documents(directions: Iterable[Any], version: str) -> Iterator[Document]:
    for direction in directions:
        raw = getattr(direction, "data", None) or {}
        body = " ".join(
            part
            for part in (
                str(raw.get("description") or ""),
                " ".join(str(item) for item in (getattr(direction, "aliases", None) or [])),
            )
            if part
        )
        yield Document(
            doc_id=getattr(direction, "direction_id", ""),
            kind="direction",
            title=getattr(direction, "canonical_name", "") or "",
            body=body,
            source="otheloo",
            source_version=version,
            metadata={"taxonomy": getattr(direction, "taxonomy", "")},
        )


def build_documents(
    *,
    directions: Iterable[Any],
    occupations: Iterable[Any],
    formations: Iterable[Any],
    competences: Iterable[dict[str, Any]] = (),
    version: str,
    max_competences: int = 4000,
) -> DocumentBatch:
    """Construit le corpus. Les competences sont plafonnees et echantillonnees.

    19 479 competences brutes submergeaient l'index et n'apporteraient rien si
    on garde tout : on garde un echantillon deterministe (pas aleatoire) pour
    garder la reproductibilite du build.
    """
    documents: list[Document] = [
        *_direction_documents(directions, version),
        *_occupation_documents(occupations, version),
        *_formation_documents(formations, version),
    ]

    selected = list(competences)
    if len(selected) > max_competences:
        stride = len(selected) / max_competences
        selected = [selected[int(index * stride)] for index in range(max_competences)]
    for competence in selected:
        label = str(competence.get("label") or "")
        if not label:
            continue
        documents.append(
            Document(
                doc_id=f"comp-{abs(hash((competence.get('domaine') or '', label))) % 10**10}",
                kind="competence",
                title=label,
                body=" ".join(str(competence.get(key) or "") for key in ("macro_competence", "objectif", "enjeu", "domaine")),
                source="rome",
                source_version=str(competence.get("source_version") or version),
                metadata={"domaine": competence.get("domaine")},
            )
        )

    return DocumentBatch(documents=[document for document in documents if document.doc_id and document.title])
