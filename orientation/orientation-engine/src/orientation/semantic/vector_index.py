from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

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
        if len(ids) == 0:
            raise ValueError("vector index cannot be empty")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        self._vectors = np.asarray(
            vectors / np.maximum(norms, 1e-12),
            dtype=np.float32,
        )
        self._ids = list(ids)

    def save(self, path: Path) -> None:
        if self._vectors.size == 0:
            raise RuntimeError("cannot persist an empty vector index")
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path,
            ids=np.asarray(self._ids, dtype=str),
            vectors=self._vectors,
        )

    def load(self, path: Path) -> None:
        with np.load(path, allow_pickle=False) as payload:
            ids = payload["ids"].astype(str).tolist()
            vectors = np.asarray(payload["vectors"], dtype=np.float32)
        self.fit(ids, vectors)

    def search(self, query: np.ndarray, k: int = 10) -> list[VectorMatch]:
        if self._vectors.size == 0:
            return []
        if k < 1:
            raise ValueError("k must be positive")
        query_vector = np.asarray(query, dtype=np.float32)
        if query_vector.ndim != 1 or query_vector.shape[0] != self._vectors.shape[1]:
            raise ValueError("query vector has the wrong dimension")
        norm = float(np.linalg.norm(query_vector))
        normalized = query_vector / max(norm, 1e-12)
        scores = self._vectors @ normalized
        order = np.argsort(-scores)[:k]
        return [VectorMatch(self._ids[int(index)], float(scores[int(index)])) for index in order]
