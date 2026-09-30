from dataclasses import dataclass
import numpy as np
from orientation.psychometrics.estimation import estimate_trait, item_information

@dataclass(frozen=True)
class CATResult:
    theta: float
    standard_error: float
    administered_items: tuple[str, ...]
    stopped: bool

class TwoPLCAT:
    def __init__(self, item_ids: list[str], discrimination: np.ndarray, difficulty: np.ndarray,
                 target_se: float = 0.30, max_items: int = 30) -> None:
        if len(item_ids) != len(discrimination) or len(item_ids) != len(difficulty):
            raise ValueError("item bank arrays must align")
        self.item_ids = item_ids
        self.a = discrimination
        self.b = difficulty
        self.target_se = target_se
        self.max_items = max_items

    def run(self, responses: np.ndarray) -> CATResult:
        if len(responses) < 1 or len(responses) > self.max_items:
            raise ValueError("responses length outside CAT bounds")
        n = len(responses)
        theta = estimate_trait(responses, self.a[:n], self.b[:n])
        info = sum(item_information(theta, float(a), float(b))
                   for a, b in zip(self.a[:n], self.b[:n]))
        se = float(1.0 / np.sqrt(max(info, 1e-9)))
        return CATResult(theta, se, tuple(self.item_ids[:n]), se <= self.target_se)
