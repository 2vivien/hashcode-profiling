from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class BanditAction:
    action_id: str
    score: float
    propensity: float

class LinUCB:
    def __init__(self, dimension: int, alpha: float = 1.0) -> None:
        if dimension <= 0:
            raise ValueError("dimension must be positive")
        self.dimension = dimension
        self.alpha = alpha
        self.a_inv: dict[str, np.ndarray] = {}
        self.b: dict[str, np.ndarray] = {}

    def _ensure(self, action_id: str) -> None:
        if action_id not in self.a_inv:
            self.a_inv[action_id] = np.eye(self.dimension)
            self.b[action_id] = np.zeros(self.dimension)

    def select(self, contexts: dict[str, np.ndarray]) -> BanditAction:
        if not contexts:
            raise ValueError("contexts cannot be empty")
        values = []
        for action_id, x in contexts.items():
            self._ensure(action_id)
            inv = self.a_inv[action_id]
            theta = inv @ self.b[action_id]
            mean = float(theta @ x)
            uncertainty = float(np.sqrt(max(x @ inv @ x, 0.0)))
            values.append(BanditAction(action_id, mean + self.alpha * uncertainty,
                                       1.0 / len(contexts)))
        return max(values, key=lambda item: item.score)

    def update(self, action_id: str, context: np.ndarray, reward: float) -> None:
        self._ensure(action_id)
        inv = self.a_inv[action_id]
        a = np.linalg.inv(inv) + np.outer(context, context)
        self.a_inv[action_id] = np.linalg.inv(a)
        self.b[action_id] += reward * context
