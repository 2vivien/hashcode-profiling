"""Registre des modèles appris : artefacts, métadonnées, disponibilité.

Un moteur appris n'existe que s'il y a un **artefact sur disque** décrivant son
version, ses hyper-paramètres et sa date d'entraînement. Sans artefact, la couche
est simplement inactive — et elle le dit, au lieu de produire un score qui aurait
l'air d'être le résultat d'un entraînement.

Emplacement : `data/runtime/models/` (volume runtime, gitignoré). Un modèle
entraîné est un résultat reproductible, pas du code : il se versionne, se
ré-audit et se remplace sans redéploiement de code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MODEL_ROOT = Path("data/runtime/models")


@dataclass(frozen=True)
class ModelArtifact:
    """Ce qu'on sait d'un modèle sans l'avoir chargé."""

    task: str
    version: str
    path: Path
    trained_at: str | None = None
    training_samples: int = 0
    metrics: dict[str, float] = field(default_factory=dict)
    training_data_version: str | None = None

    @property
    def available(self) -> bool:
        return self.path.is_file()

    def describe(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "version": self.version,
            "available": self.available,
            "trained_at": self.trained_at,
            "training_samples": self.training_samples,
            "metrics": self.metrics,
            "training_data_version": self.training_data_version,
        }


class ModelRegistry:
    """Lit `*.meta.json` et expose les artefacts par tâche."""

    def __init__(self, root: Path = MODEL_ROOT) -> None:
        self.root = root

    def tasks(self) -> list[str]:
        if not self.root.is_dir():
            return []
        return sorted({path.stem.removesuffix(".meta") for path in self.root.glob("*.meta.json")})

    def get(self, task: str) -> ModelArtifact | None:
        meta = self.root / f"{task}.meta.json"
        if not meta.is_file():
            return None
        try:
            payload: dict[str, Any] = json.loads(meta.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        payload_path = self.root / f"{task}.json"
        return ModelArtifact(
            task=task,
            version=str(payload.get("version") or "unknown"),
            path=payload_path,
            trained_at=payload.get("trained_at"),
            training_samples=int(payload.get("training_samples") or 0),
            metrics={str(k): float(v) for k, v in (payload.get("metrics") or {}).items()},
            training_data_version=payload.get("training_data_version"),
        )

    def require(self, task: str) -> ModelArtifact:
        artifact = self.get(task)
        if artifact is None or not artifact.available:
            raise FileNotFoundError(f"aucun modèle entraîné pour la tâche « {task} » dans {self.root}")
        return artifact

    def describe(self) -> list[dict[str, Any]]:
        return [artifact.describe() for task in self.tasks() if (artifact := self.get(task)) is not None]

    def register(
        self,
        task: str,
        payload: dict[str, Any],
        *,
        version: str,
        trained_at: str,
        training_samples: int,
        metrics: dict[str, float] | None = None,
        training_data_version: str | None = None,
    ) -> Path:
        """Écrit l'artefact et ses métadonnées (même opération, donc pas d'état incohérent)."""
        self.root.mkdir(parents=True, exist_ok=True)
        data_path = self.root / f"{task}.json"
        data_path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        meta = {
            "task": task,
            "version": version,
            "trained_at": trained_at,
            "training_samples": training_samples,
            "metrics": metrics or {},
            "training_data_version": training_data_version,
        }
        (self.root / f"{task}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return data_path
