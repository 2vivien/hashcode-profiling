from orientation.domain.profile.service import ProfileService


def profile_confidence(profile) -> float:
    return ProfileService().completeness(profile)
