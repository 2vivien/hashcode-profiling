from orientation.contracts.profile import StudentProfile
from orientation.recommendation.uncertainty.completeness import profile_completeness
from orientation.recommendation.uncertainty.propagation import propagate_uncertainty


class UncertaintyService:
    def calculate(self, profile: StudentProfile, confidence: float) -> float:
        assessment_confidence = profile.assessment_confidence or confidence
        return propagate_uncertainty(
            min(confidence, assessment_confidence, profile_completeness(profile))
        )
