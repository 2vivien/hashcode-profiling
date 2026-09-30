from fastapi import APIRouter
from orientation.contracts.assessment import AssessmentResult
router=APIRouter(tags=["assessments"])

@router.post("/assessments",response_model=AssessmentResult)
def create_assessment(assessment:AssessmentResult)->AssessmentResult:
    return assessment
