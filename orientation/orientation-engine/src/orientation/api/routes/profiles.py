from fastapi import APIRouter
from orientation.contracts.profile import StudentProfile
router=APIRouter(tags=["profiles"])

@router.post("/profiles",response_model=StudentProfile)
def create_profile(profile:StudentProfile)->StudentProfile:
    return profile

@router.get("/profiles/{student_id}",response_model=StudentProfile)
def get_profile(student_id:str)->StudentProfile:
    return StudentProfile(student_id=student_id)
