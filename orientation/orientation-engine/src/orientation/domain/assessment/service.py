from orientation.contracts.assessment import AssessmentResult


class AssessmentService:
    def normalize_traits(self, assessment: AssessmentResult) -> dict[str, float]:
        return {key: max(0.0, min(1.0, value)) for key, value in assessment.traits.items()}
