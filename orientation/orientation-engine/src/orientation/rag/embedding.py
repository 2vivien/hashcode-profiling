"""Embeddings : deux fournisseurs, un seul contrat.

- `GeminiEmbedder` : vrai modèle vectoriel (`text-embedding-004`), semantique
  multilingue, gratuit. Nécessite une clé.
- `HashingEmbedder` : repli **sans dépendance et sans réseau**. Hash de
  n-grammes de caractères projetés dans un vecteur dense, normalisé. Ce n'est
  pas un modèle appris, mais il est déterministe, gratuit, et suffisamment
  proche lexicalement pour servir de garde-fou : le système ne s'arrête jamais
  de fonctionner parce qu'une clé a expiré.

Le choix se fait à l'exécution, jamais dans le code appelant : si la clé est
absente ou l'API en panne, on bascule et on le dit.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from collections.abc import Sequence
from typing import Any, Protocol

import numpy as np

from orientation.infrastructure.translation.base import USER_AGENT

# `text-embedding-004` est retiré de l'API : les modèles d'embedding publiés
# sont désormais de la famille `gemini-embedding-*`. On prend la version stable,
# pas une préversion.
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:batchEmbedContents"
HASHING_DIMENSIONS = 512


class Embedder(Protocol):
    name: str

    def encode(self, texts: Sequence[str]) -> np.ndarray: ...


class EmbeddingUnavailable(RuntimeError):
    """Le fournisseur d'embeddings n'a pas pu répondre."""


def normalize_rows(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return np.asarray(matrix / np.maximum(norms, 1e-12), dtype=np.float32)


class HashingEmbedder:
    """Projection déterministe de n-grammes de caractères.

    Sert de filet : jamais de réseau, jamais de clé, même sortie à chaque
    exécution (important pour que l'index soit reproductible et testable).
    """

    name = "hashing-ngram-v1"

    def __init__(self, dimensions: int = HASHING_DIMENSIONS) -> None:
        self.dimensions = dimensions

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        matrix = np.zeros((len(texts), self.dimensions), dtype=np.float32)
        for row, text in enumerate(texts):
            padded = f"  {text.lower()}  "
            for size in (2, 3):
                for start in range(max(0, len(padded) - size + 1)):
                    gram = padded[start : start + size]
                    digest = hashlib.blake2b(gram.encode("utf8"), digest_size=8).digest()
                    bucket = int.from_bytes(digest[:4], "big") % self.dimensions
                    sign = 1.0 if digest[4] % 2 == 0 else -1.0
                    matrix[row, bucket] += sign
        return normalize_rows(matrix)


class GeminiEmbedder:
    """Embeddings Gemini : sous-ensemble par requête (l'API limite le lot)."""

    name = GEMINI_EMBEDDING_MODEL

    def __init__(
        self,
        api_key: str,
        model: str = GEMINI_EMBEDDING_MODEL,
        batch_size: int = 100,
        timeout: int = 60,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.batch_size = batch_size
        self.timeout = timeout
        self.max_retries = max_retries

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, HASHING_DIMENSIONS), dtype=np.float32)
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = list(texts[start : start + self.batch_size])
            vectors.extend(self._encode_batch(batch))
        matrix = np.asarray(vectors, dtype=np.float32)
        return normalize_rows(matrix)

    def _encode_batch(self, texts: list[str]) -> list[list[float]]:
        # L'API Gemini exige que le modèle soit rappelé sur *chaque* élément du
        # lot : l'URL ne suffit pas.
        payload = json.dumps(
            {
                "requests": [
                    {
                        "model": f"models/{self.model}",
                        "content": {"parts": [{"text": text}]},
                        "taskType": "RETRIEVAL_DOCUMENT",
                    }
                    for text in texts
                ]
            }
        ).encode()
        request = urllib.request.Request(
            GEMINI_ENDPOINT.format(model=self.model),
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key, "User-Agent": USER_AGENT},
        )

        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                # URL constante https + modèle constant : B310 sans risque ici.
                with urllib.request.urlopen(request, timeout=self.timeout) as response:  # nosec B310
                    body: dict[str, Any] = json.loads(response.read().decode())
            except urllib.error.HTTPError as error:
                last_error = error
                if error.code in (400, 401, 403, 404):
                    break
                time.sleep(2.0**attempt)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as error:
                last_error = error
                time.sleep(2.0**attempt)
            else:
                return self._extract(body, len(texts))
        raise EmbeddingUnavailable(str(last_error))

    @staticmethod
    def _extract(body: dict[str, Any], expected: int) -> list[list[float]]:
        embeddings = body.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != expected:
            raise EmbeddingUnavailable("réponse d'embeddings inexploitable")
        vectors: list[list[float]] = []
        for item in embeddings:
            values = item.get("values") if isinstance(item, dict) else None
            if not isinstance(values, list):
                raise EmbeddingUnavailable("vecteur manquant")
            vectors.append([float(value) for value in values])
        return vectors


def build_embedder(api_key: str, **overrides: Any) -> Embedder:
    """Choisit le meilleur fournisseur disponible, sans jamais échouer."""
    if api_key:
        embedder = GeminiEmbedder(api_key=api_key, **overrides)
        try:
            embedder.encode(["sonde de disponibilité"])
        except EmbeddingUnavailable:
            return HashingEmbedder()
        return embedder
    return HashingEmbedder()
