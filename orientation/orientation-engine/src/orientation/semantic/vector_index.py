import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class VectorMatch:
    document_id: str
    score: float


class NumpyVectorIndex:
    def __init__(self, index_version: str = "semantic-index-v1") -> None:
        if not index_version.strip():
            raise ValueError("index_version is required")
        self.index_version = index_version
        self._ids: list[str] = []
        self._vectors = np.empty((0, 0), dtype=np.float32)
        self._metadata: dict[str, str] = {}

    def fit(
        self,
        ids: Sequence[str],
        vectors: np.ndarray,
        metadata: dict[str, str] | None = None,
    ) -> None:
        if len(ids) != len(vectors) or vectors.ndim != 2:
            raise ValueError("ids and vectors must describe the same 2D matrix")
        if len(ids) == 0:
            raise ValueError("vector index cannot be empty")
        if not np.all(np.isfinite(vectors)):
            raise ValueError("vector matrix must contain only finite values")
        if len(set(ids)) != len(ids):
            raise ValueError("vector document ids must be unique")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        self._vectors = np.asarray(
            vectors / np.maximum(norms, 1e-12),
            dtype=np.float32,
        )
        self._ids = list(ids)
        self._metadata = dict(metadata or {})

    def save(self, path: Path) -> None:
        if self._vectors.size == 0:
            raise RuntimeError("cannot persist an empty vector index")
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path,
            ids=np.asarray(self._ids, dtype=str),
            vectors=self._vectors,
            index_version=np.asarray(self.index_version),
            metadata=np.asarray(json.dumps(self._metadata, sort_keys=True)),
        )

    def load(self, path: Path) -> None:
        with np.load(path, allow_pickle=False) as payload:
            ids = payload["ids"].astype(str).tolist()
            vectors = np.asarray(payload["vectors"], dtype=np.float32)
            stored_version = str(payload["index_version"].item())
            metadata = json.loads(str(payload["metadata"].item()))
        if stored_version != self.index_version:
            raise ValueError(
                f"vector index version mismatch: expected {self.index_version}, got {stored_version}"
            )
        if not isinstance(metadata, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in metadata.items()
        ):
            raise ValueError("invalid vector index metadata")
        self.fit(ids, vectors, metadata)

    def search(self, query: np.ndarray, k: int = 10) -> list[VectorMatch]:
        if self._vectors.size == 0:
            return []
        if k < 1:
            raise ValueError("k must be positive")
        query_vector = np.asarray(query, dtype=np.float32)
        if query_vector.ndim != 1 or query_vector.shape[0] != self._vectors.shape[1]:
            raise ValueError("query vector has the wrong dimension")
        if not np.all(np.isfinite(query_vector)):
            raise ValueError("query vector must contain only finite values")
        norm = float(np.linalg.norm(query_vector))
        normalized = query_vector / max(norm, 1e-12)
        scores = self._vectors @ normalized
        order = np.argsort(-scores)[:k]
        return [VectorMatch(self._ids[int(index)], float(scores[int(index)])) for index in order]
