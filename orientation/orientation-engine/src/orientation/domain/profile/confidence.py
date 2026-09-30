from orientation.contracts.profile import StudentProfile
from orientation.domain.profile.service import ProfileService


def profile_confidence(profile: StudentProfile) -> float:
    return ProfileService().completeness(profile)
