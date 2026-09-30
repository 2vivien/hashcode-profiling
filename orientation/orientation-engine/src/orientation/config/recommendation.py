from dataclasses import dataclass

from orientation.config.scoring import ScoringWeights

@dataclass(frozen=True)
class RecommendationConfig:
    top_k: int = 20
    final_k: int = 8
    diversification_lambda: float = 0.75
    minimum_evidence: int = 2
    weights: ScoringWeights = ScoringWeights()

    def validate(self) -> None:
        if not 1 <= self.final_k <= self.top_k:
            raise ValueError("final_k must be between 1 and top_k")
        if not 0 <= self.diversification_lambda <= 1:
            raise ValueError("diversification_lambda must be in [0, 1]")
        if self.minimum_evidence < 0:
            raise ValueError("minimum_evidence cannot be negative")
        self.weights.validate()
