"""Index lexical BM25, sans dépendance externe.

Pourquoi le faire à la main alors que `rank_bm25` existe : le contrat de
dépendances du moteur est minimal et une dépendance de plus pour un algo de
150 lignes n'est pas un bon échange. BM25 est ici une porte d'entrée **déterministe**
qui fonctionne sans réseau ni clé : la sémantique vient s'y ajouter par-dessus,
pas à sa place.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from orientation.rag.documents import Document, tokenize

K1 = 1.5
B = 0.75


@dataclass(frozen=True)
class LexicalMatch:
    doc_id: str
    score: float


class Bm25Index:
    def __init__(self, documents: Sequence[Document]) -> None:
        self._documents = list(documents)
        self._tokens = [tokenize(document.text) for document in self._documents]
        self._lengths = [len(tokens) for tokens in self._tokens]
        self._avg_length = (sum(self._lengths) / len(self._lengths)) if self._tokens else 0.0
        self._frequencies = [Counter(tokens) for tokens in self._tokens]
        document_frequency: Counter[str] = Counter()
        for tokens in self._tokens:
            document_frequency.update(set(tokens))
        total = max(1, len(self._documents))
        # IDF lissé : évite les valeurs négatives sur un corpus monolingue.
        self._idf = {term: math.log(1 + (total - count + 0.5) / (count + 0.5)) for term, count in document_frequency.items()}

    def search(self, query: str, k: int = 10) -> list[LexicalMatch]:
        terms = tokenize(query)
        if not terms:
            return []
        results: list[LexicalMatch] = []
        for index, frequencies in enumerate(self._frequencies):
            length = self._lengths[index]
            score = 0.0
            for term in terms:
                frequency = frequencies.get(term, 0)
                if not frequency:
                    continue
                idf = self._idf.get(term, 0.0)
                denominator = frequency + K1 * (1 - B + B * length / (self._avg_length or 1.0))
                score += idf * (frequency * (K1 + 1) / denominator)
            if score > 0:
                results.append(LexicalMatch(doc_id=self._documents[index].doc_id, score=score))
        results.sort(key=lambda item: (-item.score, item.doc_id))
        return results[:k]

    def __len__(self) -> int:
        return len(self._documents)
