from dataclasses import dataclass
from typing import cast

import numpy as np

from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss


@dataclass(frozen=True)
class CalibrationReport:
    brier: float
    log_loss: float
    sample_count: int


class ScoreCalibrator:
    """Maps ranking scores to probabilities only after independent calibration data."""

    def __init__(self, method: str = "sigmoid") -> None:
        if method not in {"sigmoid", "isotonic"}:
            raise ValueError("method must be sigmoid or isotonic")
        self.method = method
        self._model: object | None = None

    def fit(self, scores: np.ndarray, labels: np.ndarray) -> CalibrationReport:
        x = np.asarray(scores, dtype=np.float64)
        y = np.asarray(labels, dtype=np.int64)
        if x.ndim != 1 or y.ndim != 1 or len(x) != len(y) or len(x) < 20:
            raise ValueError("calibration requires at least 20 aligned observations")
        if not np.all(np.isin(y, (0, 1))) or len(np.unique(y)) < 2:
            raise ValueError("binary calibration labels with both classes are required")
        if self.method == "sigmoid":
            model = LogisticRegression()
            model.fit(x.reshape(-1, 1), y)
            probabilities = model.predict_proba(x.reshape(-1, 1))[:, 1]
        else:
            model = IsotonicRegression(out_of_bounds="clip")
            model.fit(x, y)
            probabilities = model.predict(x)
        self._model = model
        return CalibrationReport(
            brier=float(brier_score_loss(y, probabilities)),
            log_loss=float(log_loss(y, probabilities)),
            sample_count=len(y),
        )

    def predict(self, scores: np.ndarray) -> np.ndarray:
        if self._model is None:
            raise RuntimeError("calibrator is not fitted")
        x = np.asarray(scores, dtype=np.float64)
        if self.method == "sigmoid":
            sigmoid_model = cast(LogisticRegression, self._model)
            return np.asarray(sigmoid_model.predict_proba(x.reshape(-1, 1))[:, 1], dtype=np.float64)
        isotonic_model = cast(IsotonicRegression, self._model)
        return np.asarray(isotonic_model.predict(x), dtype=np.float64)

    def evaluate(self, scores: np.ndarray, labels: np.ndarray) -> CalibrationReport:
        y = np.asarray(labels, dtype=np.int64)
        probabilities = self.predict(scores)
        return CalibrationReport(
            brier=float(brier_score_loss(y, probabilities)),
            log_loss=float(log_loss(y, probabilities)),
            sample_count=len(y),
        )
