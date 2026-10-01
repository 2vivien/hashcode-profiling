from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

import numpy as np


class _Ranker(Protocol):
    def predict(self, X: np.ndarray) -> np.ndarray: ...


@dataclass(frozen=True)
class RankingExample:
    query_id: str
    direction_id: str
    label: float
    features: tuple[float, ...]


class LambdaMARTModel:
    def __init__(self) -> None:
        self.model: _Ranker | None = None
        self.feature_names: tuple[str, ...] = ()

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        groups: Sequence[int],
        feature_names: Sequence[str],
    ) -> None:
        from lightgbm import LGBMRanker

        matrix = np.asarray(X, dtype=np.float64)
        labels = np.asarray(y, dtype=np.float64)
        if matrix.ndim != 2 or labels.ndim != 1 or len(matrix) != len(labels):
            raise ValueError("ranking features and labels must align")
        if not groups or any(group <= 0 for group in groups) or sum(groups) != len(labels):
            raise ValueError("group sizes must be positive and sum to number of labels")
        names = tuple(feature_names)
        if len(names) != matrix.shape[1] or len(set(names)) != len(names):
            raise ValueError("feature names must uniquely match feature columns")

        model = LGBMRanker(
            objective="lambdarank",
            metric="ndcg",
            n_estimators=300,
            learning_rate=0.04,
            num_leaves=31,
            random_state=42,
        )
        model.fit(matrix, labels, group=list(groups))
        self.model = cast(_Ranker, model)
        self.feature_names = names

    def _validate_features(self, X: np.ndarray) -> np.ndarray:
        matrix = np.asarray(X, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[1] != len(self.feature_names):
            raise ValueError("prediction features do not match the trained feature schema")
        return matrix

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("LambdaMART model is not trained")
        return np.asarray(self.model.predict(self._validate_features(X)), dtype=np.float64)

    def save(self, path: Path) -> None:
        if self.model is None:
            raise RuntimeError("LambdaMART model is not trained")
        from joblib import dump

        path.parent.mkdir(parents=True, exist_ok=True)
        dump(
            {
                "model": self.model,
                "feature_names": self.feature_names,
                "model_type": "lambdamart",
                "schema_version": "ranking-features-v1",
            },
            path,
        )

    def load(self, path: Path) -> None:
        from joblib import load

        payload = load(path)
        if not isinstance(payload, dict) or "model" not in payload:
            raise ValueError("invalid LambdaMART model artifact")
        model = payload["model"]
        if not hasattr(model, "predict"):
            raise ValueError("model artifact does not expose predict")
        feature_names = payload.get("feature_names", ())
        if not isinstance(feature_names, (tuple, list)):
            raise ValueError("invalid LambdaMART feature schema")
        self.model = cast(_Ranker, model)
        self.feature_names = tuple(str(name) for name in feature_names)
