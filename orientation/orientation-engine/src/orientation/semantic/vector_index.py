from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class VectorMatch:
    document_id: str
    score: float


class NumpyVectorIndex:
    def __init__(self) -> None:
        self._ids: list[str] = []
        self._vectors = np.empty((0, 0), dtype=np.float32)

    def fit(self, ids: Sequence[str], vectors: np.ndarray) -> None:
        if len(ids) != len(vectors) or vectors.ndim != 2:
            raise ValueError("ids and vectors must describe the same 2D matrix")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        self._vectors = vectors / np.maximum(norms, 1e-12)
        self._ids = list(ids)

    def search(self, query: np.ndarray, k: int = 10) -> list[VectorMatch]:
        if self._vectors.size == 0:
            return []
        if k < 1:
            raise ValueError("k must be positive")
        q = query / max(float(np.linalg.norm(query)), 1e-12)
        scores = self._vectors @ q
        order = np.argsort(-scores)[:k]
        return [VectorMatch(self._ids[int(i)], float(scores[int(i)])) for i in order]
