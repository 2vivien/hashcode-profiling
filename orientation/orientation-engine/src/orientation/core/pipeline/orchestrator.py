from orientation.application.use_cases.generate_recommendation import GenerateRecommendation
from orientation.contracts.profile import StudentProfile
from orientation.contracts.recommendation import Recommendation


class PipelineOrchestrator:
    """Pipeline injecté — stateless, sans chemin dur au niveau module."""

    def __init__(self, recommendation_service: GenerateRecommendation):
        self.recommendation_service = recommendation_service

    def execute(self, profile: StudentProfile) -> Recommendation:
        return self.recommendation_service.execute(profile)
