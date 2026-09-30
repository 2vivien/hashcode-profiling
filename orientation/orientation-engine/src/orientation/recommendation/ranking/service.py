from orientation.contracts.recommendation import RecommendationItem
from orientation.recommendation.ranking.deterministic import DeterministicRanking


class RankingService:
    def __init__(self) -> None:
        self.strategy = DeterministicRanking()

    def rank(self, items: list[RecommendationItem]) -> list[RecommendationItem]:
        return self.strategy.rank(items)
