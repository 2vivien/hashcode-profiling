"""Pile de recommandation : déterministe + couches apprises, avec traçabilité."""

from orientation.engine.registry import ModelArtifact, ModelRegistry
from orientation.engine.stack import (
    FairnessGuard,
    LayerOutcome,
    RecommendationStack,
    ScoredCandidate,
    StackResult,
    vectorize,
)

__all__ = [
    "FairnessGuard",
    "LayerOutcome",
    "ModelArtifact",
    "ModelRegistry",
    "RecommendationStack",
    "ScoredCandidate",
    "StackResult",
    "vectorize",
]
