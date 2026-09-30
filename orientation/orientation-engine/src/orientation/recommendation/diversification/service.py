from orientation.contracts.recommendation import RecommendationItem
from orientation.recommendation.diversification.mmr import diversify


class DiversificationService:
    def diversify(
        self, items: list[RecommendationItem], final_k: int, lambda_value: float
    ) -> list[RecommendationItem]:
        return diversify(items, final_k, lambda_value)
