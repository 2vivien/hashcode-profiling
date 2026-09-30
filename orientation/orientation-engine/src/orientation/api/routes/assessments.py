from fastapi import APIRouter

from orientation.contracts.assessment import AssessmentResult
from orientation.infrastructure.persistence.assessment_repository import (
    InMemoryAssessmentRepository,
)

router = APIRouter(tags=["assessments"])
repository = InMemoryAssessmentRepository()


@router.post("/assessments", response_model=AssessmentResult)
def create_assessment(assessment: AssessmentResult) -> AssessmentResult:
    return repository.save(assessment)
