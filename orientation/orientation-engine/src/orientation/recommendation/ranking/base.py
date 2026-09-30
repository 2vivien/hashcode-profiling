from abc import ABC, abstractmethod
from orientation.contracts.recommendation import RecommendationItem

class RankingStrategy(ABC):
    @abstractmethod
    def rank(self, items: list[RecommendationItem]) -> list[RecommendationItem]:
        raise NotImplementedError
