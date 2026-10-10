"""Assemblage du contexte (« preprompting »).

Le but n'est pas de noyer le modèle sous du texte, mais de lui donner **le
bon contexte, complet et sourcé**. Trois règles :

1. **Budget explicite.** On ne déborde jamais silencieusement : si le budget est
   atteint, on dit ce qui a été écarté.
2. **Provenance obligatoire.** Chaque affirmation doit dire d'où elle vient
   (kind, doc_id, version de source). Un contexte non sourcé est
   invérifiable, donc inutilisable.
3. **Déterminisme.** Même entrée → même contexte. Le tri départage par score
   puis par identifiant : jamais par l'ordre d'un dictionnaire.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from orientation.rag.documents import Document
from orientation.rag.retriever import RetrievedDocument

# ~4 caractères par token est une estimation prudente et stable pour du texte
# français : on préfère slightly sur-dimensionner que tronquer en silence.
CHARACTERS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARACTERS_PER_TOKEN)


@dataclass(frozen=True)
class ContextBlock:
    kind: str
    doc_id: str
    title: str
    text: str
    source: str
    source_version: str
    score: float
    tokens: int

    def render(self) -> str:
        return f"[{self.kind} · {self.source} {self.source_version} · {self.doc_id}]\n{self.title}\n{self.text}".strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "doc_id": self.doc_id,
            "title": self.title,
            "source": self.source,
            "source_version": self.source_version,
            "score": self.score,
            "tokens": self.tokens,
        }


@dataclass(frozen=True)
class ContextPack:
    query: str
    blocks: list[ContextBlock]
    token_budget: int
    dropped: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def tokens(self) -> int:
        return sum(block.tokens for block in self.blocks)

    def provenance(self) -> list[str]:
        return [f"{block.kind}:{block.doc_id}@{block.source_version}" for block in self.blocks]

    def render(self) -> str:
        if not self.blocks:
            return ""
        header = f"# Contexte (requête : {self.query})"
        footer = f"\n{self.tokens}/{self.token_budget} tokens retenus"
        if self.dropped:
            footer += f", {self.dropped} document(s) écarté(s) pour budget"
        return "\n\n".join([header, *(block.render() for block in self.blocks), footer])

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "tokens": self.tokens,
            "token_budget": self.token_budget,
            "dropped": self.dropped,
            "blocks": [block.to_dict() for block in self.blocks],
            "metadata": self.metadata,
        }


class ContextBuilder:
    def __init__(self, token_budget: int = 1200, max_per_kind: int = 4) -> None:
        if token_budget <= 0:
            raise ValueError("le budget de contexte doit être positif")
        self.token_budget = token_budget
        self.max_per_kind = max_per_kind

    def build(
        self,
        query: str,
        retrieved: Sequence[RetrievedDocument],
        metadata: dict[str, Any] | None = None,
    ) -> ContextPack:
        blocks: list[ContextBlock] = []
        per_kind: dict[str, int] = {}
        dropped = 0
        spent = 0

        for hit in retrieved:
            document: Document = hit.document
            kind_count = per_kind.get(document.kind, 0)
            if kind_count >= self.max_per_kind:
                dropped += 1
                continue
            block = ContextBlock(
                kind=document.kind,
                doc_id=document.doc_id,
                title=document.title,
                text=document.body,
                source=document.source,
                source_version=document.source_version,
                score=hit.score,
                tokens=estimate_tokens(document.text),
            )
            if spent + block.tokens > self.token_budget:
                dropped += 1
                continue
            blocks.append(block)
            per_kind[document.kind] = kind_count + 1
            spent += block.tokens

        return ContextPack(
            query=query,
            blocks=blocks,
            token_budget=self.token_budget,
            dropped=dropped,
            metadata=dict(metadata or {}),
        )
