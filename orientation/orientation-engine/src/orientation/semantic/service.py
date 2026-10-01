from collections.abc import Sequence
from dataclasses import dataclass

from orientation.semantic.embeddings import SentenceTransformerEncoder
from orientation.semantic.vector_index import NumpyVectorIndex


@dataclass(frozen=True)
class SemanticCandidate:
    direction_id: str
    score: float
    evidence: str


class SemanticMatcher:
    def __init__(
        self,
        encoder: SentenceTransformerEncoder,
        index: NumpyVectorIndex,
    ) -> None:
        self.encoder = encoder
        self.index = index

    def build(
        self,
        direction_ids: Sequence[str],
        descriptions: Sequence[str],
    ) -> None:
        self.index.fit(
            direction_ids,
            self.encoder.encode_documents(descriptions),
        )

    def match(self, query: str, k: int = 10) -> list[SemanticCandidate]:
        vector = self.encoder.encode_query([query])[0]
        return [
            SemanticCandidate(
                m.document_id,
                m.score,
                "semantic embedding cosine similarity",
            )
            for m in self.index.search(vector, k)
        ]
