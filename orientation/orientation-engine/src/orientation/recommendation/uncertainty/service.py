from orientation.contracts.profile import StudentProfile
from orientation.recommendation.uncertainty.completeness import profile_completeness
from orientation.recommendation.uncertainty.propagation import propagate_uncertainty

class UncertaintyService:
    def calculate(self, profile: StudentProfile, confidence: float) -> float:
        return propagate_uncertainty(min(confidence,profile_completeness(profile)))
