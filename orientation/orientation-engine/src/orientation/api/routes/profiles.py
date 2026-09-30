from fastapi import APIRouter, HTTPException
from orientation.contracts.profile import StudentProfile
from orientation.infrastructure.persistence.profile_repository import InMemoryProfileRepository

router=APIRouter(tags=["profiles"])
repository=InMemoryProfileRepository()

@router.post("/profiles",response_model=StudentProfile)
def create_profile(profile:StudentProfile)->StudentProfile:
    return repository.save(profile)

@router.get("/profiles/{student_id}",response_model=StudentProfile)
def get_profile(student_id:str)->StudentProfile:
    profile=repository.get(student_id)
    if profile is None:
        raise HTTPException(status_code=404,detail="profile_not_found")
    return profile
