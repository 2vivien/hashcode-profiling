from orientation.contracts.recommendation import RecommendationItem
from orientation.recommendation.ranking.base import RankingStrategy

class DeterministicRanking(RankingStrategy):
    def rank(self, items: list[RecommendationItem]) -> list[RecommendationItem]:
        return sorted(items,key=lambda item:(-item.score,-item.confidence,item.direction_id))
