"""Façade RAG : index, récupération, contexte.

Un seul objet à utiliser par le moteur. Il construit l'index à la demande (et
le mémoïse), puis répond à une question par un `ContextPack` prêt à être
injecté — ou lu par un humain dans l'interface « developers ».
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from orientation.config.settings import Settings
from orientation.rag.context import ContextBuilder, ContextPack
from orientation.rag.documents import Document, build_documents
from orientation.rag.embedding import Embedder, EmbeddingUnavailable, GeminiEmbedder, HashingEmbedder
from orientation.rag.retriever import HybridRetriever, RetrievedDocument, index_summary


@dataclass(frozen=True)
class RagConfig:
    token_budget: int = 1200
    top_k: int = 8
    max_per_kind: int = 4
    max_competences: int = 4000
    cache_path: Path = Path("data/runtime/rag-index.json")
    embedder: str = "auto"


# Index construit par process. Sans ça, chaque appel à /context ré-encoderait
# tout le corpus : c'est le coût principal du RAG, pas la recherche.
_INSTANCE: dict[tuple[str, str], RagService] = {}


def _select_embedder(api_key: str, requested: str) -> Embedder:
    """Choisit l'embedder en connaissance de la question du volume.

    Mesuré : l'offre gratuite Gemini se fait *throttler* (429) dès quelques
    centaines de documents. Indexer 6 000 textes y est donc inexploitable, alors
    qu'une requête unique par utilisateur passerait sans problème. On indexe donc
    en local par défaut, et Gemini reste un choix explicite (`rag_embedder`).
    """
    if requested == "hashing" or not api_key:
        return HashingEmbedder()
    if requested == "gemini":
        return GeminiEmbedder(api_key=api_key)
    return HashingEmbedder()


class RagService:
    def __init__(self, config: RagConfig, embedder: Embedder) -> None:
        self.config = config
        self.embedder = embedder
        self._retriever: HybridRetriever | None = None

    def index(self, documents: list[Document], *, rebuild: bool = False) -> HybridRetriever:
        """Construit l'index, ou le recharge depuis le cache disque."""
        if self._retriever is not None and not rebuild:
            return self._retriever

        if not rebuild and self._load_cached(documents):
            return self._retriever  # type: ignore[return-value]

        self._retriever = HybridRetriever(documents, self.embedder)
        self._persist(documents)
        return self._retriever

    # --- persistance -------------------------------------------------

    @staticmethod
    def _fingerprint(documents: list[Document]) -> str:
        import hashlib

        digest = hashlib.sha256()
        for document in documents:
            digest.update(f"{document.doc_id}|{document.text}".encode())
        return digest.hexdigest()

    def _load_cached(self, documents: list[Document]) -> bool:
        """Réutilise les vecteurs si le corpus n'a pas bougé.

        Recalculer 20 000 embeddings à chaque démarrage coûterait cher ; on ne
        le fait que lorsque le contenu change réellement.
        """
        if not self.config.cache_path.is_file():
            return False
        try:
            payload = json.loads(self.config.cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
        if payload.get("fingerprint") != self._fingerprint(documents):
            return False
        if payload.get("embedder") != self.embedder.name:
            return False
        blob = payload.get("vectors")
        if not isinstance(blob, str) or payload.get("count") != len(documents):
            return False
        try:
            # float16 + base64 : ~8 Mo pour 6 000 documents, contre ~60 Mo en
            # JSON de flottants Python. La perte de précision est sans effet
            # observable sur un cosinus, et le cache reste lisible par un humain.
            raw = base64.b64decode(blob)
            matrix = np.frombuffer(raw, dtype=np.float16).reshape(len(documents), -1)
        except (ValueError, OSError):
            return False
        self._retriever = HybridRetriever.from_vectors(documents, self.embedder, matrix.astype("float32"))
        return True

    def _persist(self, documents: list[Document]) -> None:
        if self._retriever is None:
            return
        path = self.config.cache_path
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            vectors = self._retriever.vectors
            path.write_text(
                json.dumps(
                    {
                        "fingerprint": self._fingerprint(documents),
                        "embedder": self.embedder.name,
                        "count": len(documents),
                        "vectors": base64.b64encode(np.asarray(vectors, dtype=np.float16).tobytes()).decode("ascii"),
                    }
                ),
                encoding="utf-8",
            )
        except OSError:
            # Le cache est une optimisation : son échec ne doit rien casser.
            pass

    # --- API ---------------------------------------------------------

    def is_ready(self) -> bool:
        return self._retriever is not None

    @property
    def documents(self) -> list[Document]:
        """Corpus indexe (vide tant que l'index n'est pas construit)."""
        return self._retriever.documents if self._retriever else []

    def retrieve(self, query: str, k: int | None = None, kinds: list[str] | None = None) -> list[RetrievedDocument]:
        if self._retriever is None:
            return []
        return self._retriever.search(query, k=k or self.config.top_k, kinds=kinds)

    def context(
        self,
        query: str,
        k: int | None = None,
        metadata: dict[str, Any] | None = None,
        budget: int | None = None,
    ) -> ContextPack:
        retrieved = self.retrieve(query, k=k)
        builder = ContextBuilder(
            token_budget=budget or self.config.token_budget,
            max_per_kind=self.config.max_per_kind,
        )
        pack = builder.build(query, retrieved, metadata=metadata)
        return ContextPack(
            query=pack.query,
            blocks=pack.blocks,
            token_budget=pack.token_budget,
            dropped=pack.dropped,
            metadata={**pack.metadata, "retrieved": len(retrieved), "embedder": self.embedder.name},
        )

    def stats(self) -> dict[str, Any]:
        if self._retriever is None:
            return {"documents": 0, "by_kind": {}, "embedder": self.embedder.name, "indexed": False}
        return {**index_summary(self._retriever), "indexed": True}


def build_from_bundle(bundle: Any, settings: Settings, config: RagConfig | None = None) -> RagService:
    """Construit (ou réutilise) le service RAG pour un bundle donné.

    Mémoïsé par (version de connaissance, embedder) : reconstruire l'index à
    chaque requête coûterait cher pour un résultat identique.
    """
    resolved = config or RagConfig(
        token_budget=settings.rag_token_budget,
        top_k=settings.rag_top_k,
        embedder=settings.rag_embedder,
    )
    embedder = _select_embedder(settings.gemini_api_key, resolved.embedder)
    key = (bundle.version, embedder.name)
    cached = _INSTANCE.get(key)
    if cached is not None and cached.is_ready():
        return cached

    competences = _load_competences()
    batch = build_documents(
        directions=bundle.directions,
        occupations=bundle.occupations,
        formations=bundle.formations,
        competences=competences,
        version=bundle.version,
        max_competences=resolved.max_competences,
    )

    service = RagService(resolved, embedder)
    try:
        service.index(batch.documents)
    except EmbeddingUnavailable:
        # Quota épuisé en pleine indexation : on rebascule en local plutôt que
        # de rendre la page indisponible.
        fallback = RagService(resolved, HashingEmbedder())
        fallback.index(batch.documents, rebuild=True)
        _INSTANCE[key] = fallback
        return fallback

    _INSTANCE[key] = service
    return service


def _load_competences(path: Path | None = None) -> list[dict[str, Any]]:
    """Les competences ROME vivent a part : elles sont huge mais utile au rappel."""
    root = path or Path("data/knowledge") / os.environ.get("OTHELLOO_KNOWLEDGE_VERSION", "v3") / "competences.json"
    if not root.is_file():
        return []
    try:
        payload = json.loads(root.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return payload if isinstance(payload, list) else []
