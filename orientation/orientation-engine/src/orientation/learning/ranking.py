from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
import joblib
import numpy as np

@dataclass(frozen=True)
class RankingExample:
    query_id: str
    direction_id: str
    label: float
    features: tuple[float, ...]

class LambdaMARTModel:
    def __init__(self) -> None:
        self.model: object | None = None
        self.feature_names: tuple[str, ...] = ()

    def fit(self, X: np.ndarray, y: np.ndarray, groups: Sequence[int], feature_names: Sequence[str]) -> None:
        from lightgbm import LGBMRanker
        if sum(groups) != len(y):
            raise ValueError("group sizes must sum to number of labels")
        model = LGBMRanker(objective="lambdarank", metric="ndcg", n_estimators=300,
                           learning_rate=0.04, num_leaves=31, random_state=42)
        model.fit(X, y, group=list(groups))
        self.model = model
        self.feature_names = tuple(feature_names)

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("LambdaMART model is not trained")
        return np.asarray(self.model.predict(X), dtype=np.float64)

    def save(self, path: Path) -> None:
        if self.model is None:
            raise RuntimeError("LambdaMART model is not trained")
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "feature_names": self.feature_names}, path)

    def load(self, path: Path) -> None:
        payload = joblib.load(path)
        self.model = payload["model"]
        self.feature_names = tuple(payload["feature_names"])
