from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BanditAction:
    action_id: str
    score: float
    propensity: float


class LinUCB:
    def __init__(self, dimension: int, alpha: float = 1.0, epsilon: float = 0.05) -> None:
        if dimension <= 0:
            raise ValueError("dimension must be positive")
        if alpha < 0 or not 0 <= epsilon < 1:
            raise ValueError("alpha must be non-negative and epsilon must be in [0,1)")
        self.dimension = dimension
        self.alpha = alpha
        self.epsilon = epsilon
        self.a_inv: dict[str, np.ndarray] = {}
        self.b: dict[str, np.ndarray] = {}

    def _ensure(self, action_id: str) -> None:
        if action_id not in self.a_inv:
            self.a_inv[action_id] = np.eye(self.dimension, dtype=np.float64)
            self.b[action_id] = np.zeros(self.dimension, dtype=np.float64)

    def scores(self, contexts: dict[str, np.ndarray]) -> dict[str, float]:
        if not contexts:
            raise ValueError("contexts cannot be empty")
        scores: dict[str, float] = {}
        for action_id, context in contexts.items():
            x = np.asarray(context, dtype=np.float64)
            if x.shape != (self.dimension,):
                raise ValueError("context has the wrong dimension")
            self._ensure(action_id)
            inv = self.a_inv[action_id]
            theta = inv @ self.b[action_id]
            mean = float(theta @ x)
            uncertainty = float(np.sqrt(max(x @ inv @ x, 0.0)))
            scores[action_id] = mean + self.alpha * uncertainty
        return scores

    def select(
        self,
        contexts: dict[str, np.ndarray],
        rng: np.random.Generator | None = None,
    ) -> BanditAction:
        scores = self.scores(contexts)
        generator = rng or np.random.default_rng()
        action_ids = list(scores)
        greedy = max(action_ids, key=lambda action_id: scores[action_id])
        if generator.random() < self.epsilon:  # noqa: SIM108
            chosen = action_ids[int(generator.integers(len(action_ids)))]
        else:
            chosen = greedy
        n = len(action_ids)
        propensity = self.epsilon / n
        if chosen == greedy:
            propensity += 1.0 - self.epsilon
        return BanditAction(chosen, scores[chosen], propensity)

    def update(self, action_id: str, context: np.ndarray, reward: float) -> None:
        x = np.asarray(context, dtype=np.float64)
        if x.shape != (self.dimension,):
            raise ValueError("context has the wrong dimension")
        if not np.isfinite(reward):
            raise ValueError("reward must be finite")
        self._ensure(action_id)
        inv = self.a_inv[action_id]
        inv_x = inv @ x
        denominator = 1.0 + float(x @ inv_x)
        self.a_inv[action_id] = inv - np.outer(inv_x, inv_x) / denominator
        self.b[action_id] += reward * x
