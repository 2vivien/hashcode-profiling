from pathlib import Path

from fastapi import APIRouter

from orientation.application.use_cases.generate_recommendation import GenerateRecommendation
from orientation.contracts.profile import StudentProfile
from orientation.contracts.recommendation import Recommendation

router = APIRouter(tags=["recommendations"])
engine = GenerateRecommendation(Path(__file__).resolve().parents[4] / "data" / "knowledge" / "v1")


@router.post("/recommendations", response_model=Recommendation)
def generate_recommendation(profile: StudentProfile) -> Recommendation:
    return engine.execute(profile)
