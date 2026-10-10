"""Passerelle entre l'évaluation V1 et la psychométrie (IRT / CAT).

L'évaluation V1 fait de l'**agrégation heuristique** : elle moyenne des valeurs
auto-déclarées. C'est honnête et ça marche, mais ce n'est pas de la
psychométrie : on ne peut pas parler de niveau latent ni d'erreur de mesure.

Brancher l'IRT ici permet deux choses :

1. quand la banque d'items est **calibrée** (paramètres 2PL disponibles), on
   estime un vrai niveau latent par MIRT, avec son erreur standard ;
2. quand elle ne l'est pas — notre cas — on dit clairement qu'on retombe sur
   l'agrégateur, au lieu de produire un nombre qui prétendrait être un niveau.

Le pont ne modifie jamais la sortie du moteur : il l'enrichit et rend compte.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from orientation.psychometrics.irt import estimate_mirt, information_mirt, standard_error_from_information

# Dimensions latentement distinctes estimées conjointement par le MIRT.
LATENT_DIMENSIONS = ("investigative", "artistic", "social", "enterprising", "conventional", "realistic")


@dataclass(frozen=True)
class AbilityEstimate:
    theta: dict[str, float]
    standard_error: dict[str, float]
    information: float
    method: str
    calibrated: bool

    def describe(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "calibrated": self.calibrated,
            "information": round(self.information, 6),
            "dimensions": len(self.theta),
        }


@dataclass(frozen=True)
class ItemParameters:
    """Paramètres 2PL d'un item : discrimination (a) et difficulté (b)."""

    discrimination: np.ndarray
    difficulty: np.ndarray


class ItemBank:
    """Banque d'items calibrée, chargée depuis le registre des modèles."""

    def __init__(self, dimensions: tuple[str, ...] = LATENT_DIMENSIONS) -> None:
        self.dimensions = dimensions
        self._parameters: dict[str, ItemParameters] = {}

    @property
    def calibrated(self) -> bool:
        return bool(self._parameters)

    @property
    def size(self) -> int:
        return len(self._parameters)

    def add(self, question_id: str, discrimination: list[float], difficulty: list[float]) -> None:
        if len(discrimination) != len(self.dimensions) or len(difficulty) != len(self.dimensions):
            raise ValueError("chaque item doit couvrir toutes les dimensions")
        self._parameters[question_id] = ItemParameters(
            discrimination=np.asarray(discrimination, dtype=np.float64),
            difficulty=np.asarray(difficulty, dtype=np.float64),
        )

    def matrix(self, question_ids: list[str]) -> tuple[np.ndarray, np.ndarray]:
        if not question_ids:
            raise ValueError("aucun item à assembler")
        discrimination = np.stack([self._parameters[q].discrimination for q in question_ids])
        difficulty = np.stack([self._parameters[q].difficulty for q in question_ids])
        return discrimination, difficulty

    @classmethod
    def from_registry(cls, task: str = "item_bank", root: Path | None = None) -> ItemBank:
        """Charge la banque calibrée si elle existe ; sinon renvoie une banque vide."""
        from orientation.engine.registry import ModelRegistry

        registry = ModelRegistry(root) if root else ModelRegistry()
        artifact = registry.get(task)
        bank = cls()
        if artifact is None or not artifact.available:
            return bank
        import json

        try:
            payload = json.loads(artifact.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return bank
        dimensions = tuple(payload.get("dimensions") or bank.dimensions)
        bank = cls(dimensions=dimensions)
        for question_id, item in (payload.get("items") or {}).items():
            try:
                bank.add(question_id, item["a"], item["b"])
            except (KeyError, TypeError, ValueError):
                continue
        return bank


def estimate_abilities(
    responses: dict[str, float],
    bank: ItemBank,
    *,
    fallback: dict[str, float] | None = None,
    max_iterations: int = 60,
) -> AbilityEstimate:
    """Estime les niveaux latents ; à défaut de banque calibrée, renvoie l'agrégat.

    `responses` associe un identifiant d'item à une réponse dans [0, 1]. Les
    items absents de la banque calibrée sont ignorés : on ne devine pas leurs
    paramètres.
    """
    usable = [question_id for question_id in responses if question_id in bank._parameters]
    usable = list(dict.fromkeys(usable))
    if not usable:
        return _degraded(fallback)

    discrimination, difficulty = bank.matrix(usable)
    raw = np.asarray([responses[question_id] for question_id in usable], dtype=np.float64)
    # L'IRT implémenté ici prend une difficulté **scalaire** par item : on
    # fait la moyenne des difficultés par dimension. C'est une approximation assumée, pas un
    # modèle vectoriel complet — le résultat reste un niveau latent estimé, mais
    # avec cette réserve.
    scalar_difficulty = difficulty.mean(axis=1)
    theta = estimate_mirt(raw, discrimination, scalar_difficulty, iterations=max_iterations)

    information = np.zeros((len(bank.dimensions), len(bank.dimensions)), dtype=np.float64)
    for index in range(len(usable)):
        information += information_mirt(theta, discrimination[index], float(scalar_difficulty[index]))

    errors = standard_error_from_information(information)
    return AbilityEstimate(
        theta={name: float(value) for name, value in zip(bank.dimensions, theta, strict=True)},
        standard_error={name: (float(value) if np.isfinite(value) else float("inf")) for name, value in zip(bank.dimensions, errors, strict=True)},
        information=float(np.sum(information)),
        method="mirt-2pl",
        calibrated=True,
    )


def _degraded(fallback: dict[str, float] | None) -> AbilityEstimate:
    return AbilityEstimate(
        theta=dict(fallback or {}),
        standard_error={name: float("inf") for name in (fallback or {})},
        information=0.0,
        method="heuristic-mean",
        calibrated=False,
    )
