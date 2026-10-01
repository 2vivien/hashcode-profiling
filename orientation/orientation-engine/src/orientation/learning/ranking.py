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

        if sum(groups) != len(y):
            raise ValueError("group sizes must sum to number of labels")
        model = LGBMRanker(
            objective="lambdarank",
            metric="ndcg",
            n_estimators=300,
            learning_rate=0.04,
            num_leaves=31,
            random_state=42,
        )
        model.fit(X, y, group=list(groups))
        self.model = cast(_Ranker, model)
        self.feature_names = tuple(feature_names)

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("LambdaMART model is not trained")
        return np.asarray(self.model.predict(X), dtype=np.float64)

    def save(self, path: Path) -> None:
        if self.model is None:
            raise RuntimeError("LambdaMART model is not trained")
        from joblib import dump

        path.parent.mkdir(parents=True, exist_ok=True)
        dump({"model": self.model, "feature_names": self.feature_names}, path)

    def load(self, path: Path) -> None:
        from joblib import load

        payload = load(path)
        if not isinstance(payload, dict) or "model" not in payload:
            raise ValueError("invalid LambdaMART model artifact")
        model = payload["model"]
        if not hasattr(model, "predict"):
            raise ValueError("model artifact does not expose predict")
        self.model = cast(_Ranker, model)
        feature_names = payload.get("feature_names", ())
        if not isinstance(feature_names, tuple):
            feature_names = tuple(feature_names)
        self.feature_names = cast(tuple[str, ...], feature_names)
