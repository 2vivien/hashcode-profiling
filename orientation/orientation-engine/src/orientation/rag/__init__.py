"""Couche de récupération augmentée (RAG) et assemblage de contexte."""

from orientation.rag.context import ContextBlock, ContextBuilder, ContextPack
from orientation.rag.documents import Document, build_documents
from orientation.rag.embedding import Embedder, GeminiEmbedder, HashingEmbedder, build_embedder
from orientation.rag.lexical import Bm25Index
from orientation.rag.retriever import HybridRetriever, RetrievedDocument
from orientation.rag.service import RagConfig, RagService, build_from_bundle

__all__ = [
    "Bm25Index",
    "ContextBlock",
    "ContextBuilder",
    "ContextPack",
    "Document",
    "Embedder",
    "GeminiEmbedder",
    "HashingEmbedder",
    "HybridRetriever",
    "RagConfig",
    "RagService",
    "RetrievedDocument",
    "build_documents",
    "build_embedder",
    "build_from_bundle",
]
