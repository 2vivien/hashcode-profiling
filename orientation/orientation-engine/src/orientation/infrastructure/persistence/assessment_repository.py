from orientation.contracts.assessment import AssessmentResult

class InMemoryAssessmentRepository:
    def __init__(self) -> None:
        self._items: dict[str,AssessmentResult] = {}

    def save(self, assessment: AssessmentResult) -> AssessmentResult:
        self._items[assessment.session_id] = assessment
        return assessment

    def get(self, session_id: str) -> AssessmentResult | None:
        return self._items.get(session_id)
