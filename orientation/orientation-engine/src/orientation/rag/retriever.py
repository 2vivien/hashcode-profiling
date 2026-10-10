"""Récupération hybride : BM25 + vecteurs, fusionnés par rang réciproque.

On ne choisit pas « lexical *ou* sémantique ». Chaque voie échoue différemment :
BM25 rate les reformulations, le cosinus rate les correspondances exactes de
codes. La fusion RRF combine les **rangs**, pas les scores — les deux échelles
n'étant pas comparables, additionner des scores bruts donnerait le poids au
fournisseur le plus bavard.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

from orientation.rag.documents import Document
from orientation.rag.embedding import Embedder, normalize_rows
from orientation.rag.lexical import Bm25Index

RRF_K = 60  # constante classique de la fusion RRF


@dataclass(frozen=True)
class RetrievedDocument:
    document: Document
    score: float
    lexical_rank: int | None
    semantic_rank: int | None

    def provenance(self) -> str:
        return self.document.provenance()


class HybridRetriever:
    def __init__(
        self,
        documents: Sequence[Document],
        embedder: Embedder,
        candidate_pool: int = 30,
    ) -> None:
        if not documents:
            raise ValueError("un index de récupération ne peut pas être vide")
        self.documents = list(documents)
        self.embedder = embedder
        self.candidate_pool = candidate_pool
        self.lexical = Bm25Index(self.documents)
        self._by_id = {document.doc_id: document for document in self.documents}
        matrix = embedder.encode([document.text for document in self.documents])
        self._vectors = normalize_rows(matrix)
        self._positions = {document.doc_id: index for index, document in enumerate(self.documents)}

    @classmethod
    def from_vectors(
        cls,
        documents: Sequence[Document],
        embedder: Embedder,
        matrix: np.ndarray,
        candidate_pool: int = 30,
    ) -> HybridRetriever:
        """Reconstruit un index depuis des vecteurs déjà calculés (cache disque)."""
        if matrix.ndim != 2 or len(matrix) != len(documents):
            raise ValueError("les vecteurs doivent correspondre aux documents")
        instance = cls.__new__(cls)
        instance.documents = list(documents)
        instance.embedder = embedder
        instance.candidate_pool = candidate_pool
        instance.lexical = Bm25Index(instance.documents)
        instance._by_id = {document.doc_id: document for document in instance.documents}
        instance._vectors = normalize_rows(matrix)
        instance._positions = {document.doc_id: index for index, document in enumerate(instance.documents)}
        return instance

    def search(self, query: str, k: int = 8, kinds: Sequence[str] | None = None) -> list[RetrievedDocument]:
        lexical_hits = self.lexical.search(query, k=self.candidate_pool)
        semantic_hits = self._semantic_search(query, self.candidate_pool)

        ranks: dict[str, tuple[int | None, int | None]] = {}
        for position, hit in enumerate(lexical_hits):
            known_lexical, known_semantic = ranks.get(hit.doc_id, (None, None))
            ranks[hit.doc_id] = (position + 1, known_semantic)
        for position, (hit_id, _score) in enumerate(semantic_hits):
            known_lexical, known_semantic = ranks.get(hit_id, (None, None))
            ranks[hit_id] = (known_lexical, position + 1)

        fused: list[tuple[float, str]] = []
        for candidate_id, (lexical_rank, semantic_rank) in ranks.items():
            score = 0.0
            if lexical_rank:
                score += 1.0 / (RRF_K + lexical_rank)
            if semantic_rank:
                score += 1.0 / (RRF_K + semantic_rank)
            fused.append((score, candidate_id))

        fused.sort(key=lambda item: (-item[0], item[1]))
        results: list[RetrievedDocument] = []
        for score, candidate_id in fused[: max(1, k * 3)]:
            document = self._by_id.get(candidate_id)
            entry = ranks.get(candidate_id)
            if document is None or entry is None:
                continue
            if kinds and document.kind not in kinds:
                continue
            lexical_rank, semantic_rank = entry
            results.append(
                RetrievedDocument(
                    document=document,
                    score=round(score, 6),
                    lexical_rank=lexical_rank,
                    semantic_rank=semantic_rank,
                )
            )
            if len(results) >= k:
                break
        return results

    def _semantic_search(self, query: str, k: int) -> list[tuple[str, float]]:
        vector = self.embedder.encode([query])[0]
        norms = np.linalg.norm(vector)
        if norms <= 1e-12:
            return []
        scores = self._vectors @ vector
        order = np.argsort(-scores)[:k]
        return [(self.documents[index].doc_id, float(scores[index])) for index in order]

    @property
    def vectors(self) -> np.ndarray:
        return self._vectors

    def documents_for(self, doc_ids: Sequence[str]) -> list[Document]:
        return [self._by_id[doc_id] for doc_id in doc_ids if doc_id in self._by_id]

    def __len__(self) -> int:
        return len(self.documents)


def index_summary(retriever: HybridRetriever) -> dict[str, Any]:
    kinds: dict[str, int] = {}
    for document in retriever.documents:
        kinds[document.kind] = kinds.get(document.kind, 0) + 1
    return {
        "documents": len(retriever),
        "by_kind": kinds,
        "embedder": retriever.embedder.name,
        "dimensions": int(retriever.vectors.shape[1]) if retriever.vectors.size else 0,
    }
