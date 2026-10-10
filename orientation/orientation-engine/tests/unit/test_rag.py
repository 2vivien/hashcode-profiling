"""La couche RAG : rappel, fusion, budget de contexte, dégradation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from orientation.rag.context import ContextBuilder, estimate_tokens
from orientation.rag.documents import Document, build_documents, normalize, tokenize
from orientation.rag.embedding import HashingEmbedder, build_embedder
from orientation.rag.lexical import Bm25Index
from orientation.rag.retriever import HybridRetriever
from orientation.rag.service import RagConfig, RagService


def doc(doc_id: str, title: str, body: str = "", kind: str = "occupation") -> Document:
    return Document(doc_id=doc_id, kind=kind, title=title, body=body, source="rome", source_version="2026-06")


@pytest.fixture
def corpus() -> list[Document]:
    return [
        doc("rome-a1101", "Conducteur / Conductrice d'engins agricoles", "Agriculture, engins"),
        doc("rome-a1102", "Infirmier / Infirmière de prévention", "Santé, soins"),
        doc("rome-a1103", "Développeur logiciel", "Informatique, développement"),
        doc("rome-a1104", "Technicien réseaux mobiles", "Télécoms, réseaux"),
        doc("rome-a1105", "Ingénieur / Ingénieure réseaux", "Télécoms, infrastructures"),
        doc("dir-data", "Data science", kind="direction"),
        doc("form-1", "Licence Informatique", kind="formation"),
    ]


# --- documents -----------------------------------------------------


def test_normalize_ignores_accents_and_case() -> None:
    assert normalize("Infirmière") == "infirmiere"
    assert "reseaux" in tokenize("Réseaux Mobiles")


def test_build_documents_skips_entries_without_title(corpus: list[Document]) -> None:
    batch = build_documents(
        directions=[],
        occupations=[],
        formations=[],
        version="v3",
    )
    assert len(batch) == 0
    assert all(document.doc_id and document.title for document in batch.documents)


# --- lexical -------------------------------------------------------


def test_bm25_prefers_exact_terms(corpus: list[Document]) -> None:
    index = Bm25Index(corpus)
    hits = index.search("infirmier", k=3)
    assert hits and hits[0].doc_id == "rome-a1102"


def test_bm25_ignores_accents(corpus: list[Document]) -> None:
    index = Bm25Index(corpus)
    assert index.search("réseaux", k=3)[0].doc_id in {"rome-a1104", "rome-a1105"}


def test_bm25_empty_query_returns_nothing(corpus: list[Document]) -> None:
    assert Bm25Index(corpus).search("   ") == []


# --- embeddings ----------------------------------------------------


def test_hashing_embedder_is_deterministic_and_normalized() -> None:
    embedder = HashingEmbedder()
    first = embedder.encode(["réseau", "réseau"])
    assert first.shape == (2, embedder.dimensions)
    assert np.allclose(first[0], first[1])
    assert pytest.approx(1.0, abs=1e-5) == float(np.linalg.norm(first[0]))


def test_hashing_embedder_separates_unrelated_texts() -> None:
    vectors = HashingEmbedder().encode(["réseau informatique", "développeur logiciel", "infirmière"])
    assert float(vectors[0] @ vectors[1]) < float(vectors[0] @ vectors[2])


def test_build_embedder_falls_back_without_key() -> None:
    assert isinstance(build_embedder(""), HashingEmbedder)


# --- récupération hybride -----------------------------------------


def test_hybrid_retriever_finds_the_right_document(corpus: list[Document]) -> None:
    retriever = HybridRetriever(corpus, HashingEmbedder())
    hits = retriever.search("devenir infirmier", k=3)
    assert hits
    assert hits[0].document.doc_id == "rome-a1102"


def test_hybrid_retriever_respects_kind_filter(corpus: list[Document]) -> None:
    retriever = HybridRetriever(corpus, HashingEmbedder())
    hits = retriever.search("réseaux", k=5, kinds=["direction"])
    assert hits and all(hit.document.kind == "direction" for hit in hits)


def test_hybrid_retriever_rejects_empty_corpus() -> None:
    with pytest.raises(ValueError):
        HybridRetriever([], HashingEmbedder())


def test_results_are_deterministic(corpus: list[Document]) -> None:
    retriever = HybridRetriever(corpus, HashingEmbedder())
    first = [hit.document.doc_id for hit in retriever.search("réseaux", k=4)]
    second = [hit.document.doc_id for hit in retriever.search("réseaux", k=4)]
    assert first == second


def test_from_vectors_roundtrip(corpus: list[Document]) -> None:
    embedder = HashingEmbedder()
    matrix = embedder.encode([document.text for document in corpus])
    rebuilt = HybridRetriever.from_vectors(corpus, embedder, matrix)
    assert len(rebuilt) == len(corpus)
    assert rebuilt.search("infirmier", k=1)[0].document.doc_id == "rome-a1102"


# --- contexte ------------------------------------------------------


def test_context_respects_token_budget(corpus: list[Document]) -> None:
    retriever = HybridRetriever(corpus, HashingEmbedder())
    hits = retriever.search("réseaux", k=7)
    pack = ContextBuilder(token_budget=40, max_per_kind=10).build("réseaux", hits)
    assert pack.tokens <= 40
    # Ce qui est écarté doit être dit, pas silencieusement perdu.
    assert pack.dropped > 0


def test_context_never_truncates_a_block(corpus: list[Document]) -> None:
    """Un budget trop petit n'autorise aucun bloc : rien ne doit être coupé au milieu."""
    retriever = HybridRetriever(corpus, HashingEmbedder())
    hits = retriever.search("réseaux", k=7)
    pack = ContextBuilder(token_budget=1, max_per_kind=10).build("réseaux", hits)
    assert pack.blocks == []
    assert pack.dropped == len(hits)


def test_context_limits_per_kind(corpus: list[Document]) -> None:
    retriever = HybridRetriever(corpus, HashingEmbedder())
    hits = retriever.search("réseaux", k=7)
    pack = ContextBuilder(token_budget=10_000, max_per_kind=1).build("réseaux", hits)
    kinds = [block.kind for block in pack.blocks]
    assert len(kinds) == len(set(kinds))


def test_context_carries_provenance(corpus: list[Document]) -> None:
    retriever = HybridRetriever(corpus, HashingEmbedder())
    pack = ContextBuilder().build("réseaux", retriever.search("réseaux", k=3))
    assert all("@2026-06" in entry for entry in pack.provenance())
    assert "Contexte" in pack.render()
    assert pack.to_dict()["blocks"][0]["source"] == "rome"


def test_context_builder_rejects_zero_budget() -> None:
    with pytest.raises(ValueError):
        ContextBuilder(token_budget=0)


def test_estimate_tokens_is_positive() -> None:
    assert estimate_tokens("x") == 1


# --- service -------------------------------------------------------


def test_service_indexes_and_reports(corpus: list[Document], tmp_path: Path) -> None:
    service = RagService(RagConfig(cache_path=tmp_path / "idx.json"), HashingEmbedder())
    service.index(corpus)
    stats = service.stats()
    assert stats["indexed"] is True
    assert stats["documents"] == len(corpus)
    assert stats["by_kind"]["occupation"] == 5


def test_service_reuses_vector_cache(corpus: list[Document], tmp_path: Path) -> None:
    cache = tmp_path / "idx.json"
    first = RagService(RagConfig(cache_path=cache), HashingEmbedder())
    first.index(corpus)
    assert cache.is_file()
    payload = json.loads(cache.read_text(encoding="utf-8"))
    assert payload["embedder"] == "hashing-ngram-v1"
    assert payload["count"] == len(corpus)
    # Vecteurs compacts : base64 de float16 (2 octets/valeur) et non une liste
    # de flottants JSON, qui coûterait au minimum une dizaine d'octets par valeur.
    assert isinstance(payload["vectors"], str)
    assert cache.stat().st_size < len(corpus) * 512 * 8

    calls = {"count": 0}
    original = HashingEmbedder.encode

    def counting(self: HashingEmbedder, texts: object) -> np.ndarray:
        calls["count"] += 1
        return original(self, texts)  # type: ignore[arg-type]

    second = RagService(RagConfig(cache_path=cache), HashingEmbedder())
    HashingEmbedder.encode = counting  # type: ignore[method-assign]
    try:
        second.index(corpus)
    finally:
        HashingEmbedder.encode = original  # type: ignore[method-assign]
    assert calls["count"] == 0  # vecteurs relus du cache, aucun appel


def test_service_reindexes_when_corpus_changes(corpus: list[Document], tmp_path: Path) -> None:
    cache = tmp_path / "idx.json"
    RagService(RagConfig(cache_path=cache), HashingEmbedder()).index(corpus)
    extended = [*corpus, doc("rome-new", "Ingénieur son")]
    service = RagService(RagConfig(cache_path=cache), HashingEmbedder())
    service.index(extended)
    assert service.stats()["documents"] == len(extended)


def test_service_without_index_returns_nothing(tmp_path: Path) -> None:
    service = RagService(RagConfig(cache_path=tmp_path / "idx.json"), HashingEmbedder())
    assert service.retrieve("réseaux") == []
    assert service.stats()["indexed"] is False
