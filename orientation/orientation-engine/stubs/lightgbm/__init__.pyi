from collections.abc import Sequence

import numpy as np


class LGBMRanker:
    def __init__(
        self,
        objective: str,
        metric: str,
        n_estimators: int,
        learning_rate: float,
        num_leaves: int,
        random_state: int,
    ) -> None: ...
    def fit(self, X: np.ndarray, y: np.ndarray, group: Sequence[int]) -> None: ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...
