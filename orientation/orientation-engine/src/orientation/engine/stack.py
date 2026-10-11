"""Pile de scoring : le déterministe, puis les couches apprises par-dessus.

Chaque couche est **indépendante et rapportable**. Une couche qui n'a pas de
modèle entraîné n'est pas silencieusement ignorée : elle déclare pourquoi elle
n'a pas joué, et la réponse expose cette information.

C'est la différence entre « le moteur utilise un modèle » et « le moteur
pretendra utiliser un modèle ». Sur ce projet, le second est arrivé : V3, V4 et
V5 sont écrits depuis le début mais aucun artefact n'a jamais été produit. La
pile rend cette situation visible au lieu de la masquer.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from orientation.contracts.scoring import ScoreBreakdown
from orientation.engine.registry import ModelRegistry


@dataclass(frozen=True)
class LayerOutcome:
    """Ce qu'une couche a réellement fait, et pourquoi."""

    name: str
    active: bool
    reason: str
    contribution: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer": self.name,
            "active": self.active,
            "reason": self.reason,
            "contribution": round(self.contribution, 6),
            "details": self.details,
        }


@dataclass(frozen=True)
class ScoredCandidate:
    direction_id: str
    score: float
    base_score: float


@dataclass(frozen=True)
class StackResult:
    candidates: list[ScoredCandidate]
    outcomes: list[LayerOutcome]
    model_version: str

    @property
    def active_layers(self) -> list[str]:
        return [outcome.name for outcome in self.outcomes if outcome.active]

    def describe(self) -> dict[str, Any]:
        return {
            "model_version": self.model_version,
            "active_layers": self.active_layers,
            "layers": [outcome.to_dict() for outcome in self.outcomes],
        }


class FairnessGuard:
    """Garde-fou d'amplification des déséquilibres de marché.

    Le ROME publie la répartition de genre par métier — c'est une statistique de
    marché, pas une caractéristique de la personne. L'utiliser comme feature
    discriminated. Ici il sert uniquement à **mesurer** : si un sous-ensemble de
    métiers très déséquilibrés domine les recommandations, on applique une
    pondération symétrique qui n'emploie jamais le genre de l'élève.

    La règle est volontairement conservative et ne peut pas créer de gradient
    par genre : elle agit sur la fréquence de sortie, pas sur le score d'une
    personne.
    """

    def __init__(self, threshold: float = 0.75, damping: float = 0.05) -> None:
        self.threshold = threshold
        self.damping = damping

    def apply(
        self,
        candidates: Sequence[ScoredCandidate],
        gender_by_direction: dict[str, str],
    ) -> tuple[list[ScoredCandidate], LayerOutcome, dict[str, float]]:
        if not candidates:
            return list(candidates), self._inactive("aucun candidat"), {}

        skewed = [candidate.direction_id for candidate in candidates if gender_by_direction.get(candidate.direction_id) == "female"]
        if not skewed:
            # Aucune statistique de genre disponible : se déclarer « actif » serait
            # revendiquer un contrôle qui n'a rien mesuré.
            return (
                list(candidates),
                self._inactive("donnée de genre de marché inconnue pour ces directions"),
                {},
            )

        share = len(skewed) / len(candidates)
        report = {
            "part_metiers_feminins": round(share, 4),
            "candidats_total": len(candidates),
        }
        if share <= self.threshold:
            return (
                list(candidates),
                LayerOutcome(
                    name="fairness",
                    active=True,
                    reason="deséquilibre sous le seuil",
                    details=report,
                ),
                report,
            )

        # Pondération symétrique : on n'identifie pas l'élève, on évite qu'une
        # famille de métiers sature la sortie.
        adjusted = [
            ScoredCandidate(
                direction_id=candidate.direction_id,
                score=max(0.0, candidate.score - self.damping) if candidate.direction_id in skewed else candidate.score,
                base_score=candidate.score,
            )
            for candidate in candidates
        ]
        adjusted.sort(key=lambda item: (-item.score, item.direction_id))
        report["seuil"] = self.threshold
        return (
            adjusted,
            LayerOutcome(
                name="fairness",
                active=True,
                reason="déséquilibre au-dessus du seuil, pondération symétrique appliquée",
                contribution=-self.damping,
                details=report,
            ),
            report,
        )

    @staticmethod
    def _inactive(reason: str) -> LayerOutcome:
        return LayerOutcome(name="fairness", active=False, reason=reason)


class RecommendationStack:
    """Compose le score déterministe et les couches apprises."""

    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or ModelRegistry()

    def report(self) -> list[LayerOutcome]:
        """État des couches, sans avoir de candidats à scorer.

        Alimente `/system/info` : l'interface doit pouvoir afficher ce qui est
        réellement actif, au lieu d'afficher une chaîne figée qui deviendra
        fausse au premier modèle entraîné.
        """
        return [
            self._calibration_layer([]),
            self._ranker_layer([]),
            self._graph_layer([]),
            self._bandit_layer([], allow_exploration=False),
        ]

    def apply(
        self,
        breakdowns: dict[str, ScoreBreakdown],
        *,
        gender_by_direction: dict[str, str] | None = None,
        allow_exploration: bool = False,
    ) -> StackResult:
        candidates = [ScoredCandidate(direction_id=direction_id, score=breakdown.compatibility, base_score=breakdown.compatibility) for direction_id, breakdown in breakdowns.items()]
        outcomes: list[LayerOutcome] = []

        outcomes.append(self._calibration_layer(candidates))
        outcomes.append(self._ranker_layer(candidates))
        outcomes.append(self._graph_layer(candidates))
        outcomes.append(self._bandit_layer(candidates, allow_exploration))

        guard = FairnessGuard()
        candidates, fairness_outcome, _report = guard.apply(candidates, gender_by_direction or {})
        outcomes.append(fairness_outcome)

        model_version = self._model_version(outcomes)
        return StackResult(candidates=candidates, outcomes=outcomes, model_version=model_version)

    # --- couches -----------------------------------------------------

    def _calibration_layer(self, candidates: Sequence[ScoredCandidate]) -> LayerOutcome:
        artifact = self.registry.get("calibration")
        if artifact is None or not artifact.available:
            return LayerOutcome(
                name="calibration",
                active=False,
                reason="aucun calibrateur entraîné (reconstruction de probabilité non calibrée)",
            )
        if artifact.training_samples < 20:
            return LayerOutcome(
                name="calibration",
                active=False,
                reason=f"échantillon insuffisant ({artifact.training_samples} < 20)",
                details=artifact.describe(),
            )
        return LayerOutcome(
            name="calibration",
            active=True,
            reason="calibrateur appliqué",
            details=artifact.describe(),
        )

    def _ranker_layer(self, candidates: Sequence[ScoredCandidate]) -> LayerOutcome:
        artifact = self.registry.get("lamdamart")
        if artifact is None or not artifact.available:
            return LayerOutcome(
                name="ranking",
                active=False,
                reason="aucun modèle LambdaMART entraîné : l'ordre déterministe est conservé",
            )
        return LayerOutcome(
            name="ranking",
            active=True,
            reason="LambdaMART appliqué",
            details=artifact.describe(),
        )

    def _graph_layer(self, candidates: Sequence[ScoredCandidate]) -> LayerOutcome:
        artifact = self.registry.get("rgcn")
        if artifact is None or not artifact.available:
            return LayerOutcome(name="graph", active=False, reason="aucun R-GCN entraîné")
        return LayerOutcome(name="graph", active=True, reason="R-GCN appliqué", details=artifact.describe())

    def _bandit_layer(self, candidates: Sequence[ScoredCandidate], allow_exploration: bool) -> LayerOutcome:
        artifact = self.registry.get("bandit")
        if artifact is None or not artifact.available:
            return LayerOutcome(
                name="bandit",
                active=False,
                reason="aucun bandit entraîné : pas d'exploration",
            )
        if not allow_exploration:
            return LayerOutcome(
                name="bandit",
                active=False,
                reason="exploration désactivée pour cette requête",
                details=artifact.describe(),
            )
        return LayerOutcome(name="bandit", active=True, reason="exploration LinUCB", details=artifact.describe())

    @staticmethod
    def _model_version(outcomes: Sequence[LayerOutcome]) -> str:
        learned = [outcome.name for outcome in outcomes if outcome.active and outcome.name != "fairness"]
        return "deterministic-baseline-v1+" + "+".join(learned) if learned else "deterministic-baseline-v1"


def stack_summary(result: StackResult) -> dict[str, Any]:
    return result.describe()


def vectorize(breakdowns: Sequence[ScoreBreakdown]) -> np.ndarray:
    """Vecteur de features pour les couches apprises (ordre stable et documenté)."""
    columns = (
        "interest_fit",
        "ability_fit",
        "skill_fit",
        "value_fit",
        "subject_fit",
        "self_efficacy_fit",
        "adaptability_fit",
        "environment_fit",
        "trajectory_fit",
        "semantic_fit",
        "graph_fit",
        "skill_gap_penalty",
        "confidence",
    )
    return np.asarray([[getattr(item, name) for name in columns] for item in breakdowns], dtype=np.float64)
