"""Contexte RAG exposé à l'API.

Ce n'est pas une boîte noire : la réponse dit quels documents ont été retenus,
d'où ils viennent, et ce qui a été écarté. Un contexte qu'on ne peut pas
auditer ne sert ni au modèle ni à l'explicabilité du moteur.
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from orientation.api.routes.recommendations import get_service
from orientation.config.settings import Settings, get_settings
from orientation.rag.service import build_from_bundle

router = APIRouter(tags=["rag"])


@router.get("/context")
def get_context(
    query: Annotated[str, Query(min_length=2, max_length=500)],
    k: Annotated[int, Query(ge=1, le=25)] = 8,
    budget: Annotated[int, Query(ge=100, le=8000)] = 1200,
    service: Any = Depends(get_service),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """Assemble le contexte documentaire d'une question, avec sa provenance."""
    bundle = service.knowledge()
    rag = build_from_bundle(bundle, settings)
    pack = rag.context(query, k=k, budget=budget, metadata={"knowledge_version": bundle.version})
    return {"context": pack.to_dict(), "rendered": pack.render(), "stats": rag.stats()}


@router.get("/rag/stats")
def rag_stats(
    service: Any = Depends(get_service),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    """État de l'index : documents par type et fournisseur d'embeddings."""
    bundle = service.knowledge()
    rag = build_from_bundle(bundle, settings)
    return rag.stats()
