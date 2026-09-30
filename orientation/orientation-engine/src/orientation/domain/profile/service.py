from statistics import fmean

from orientation.contracts.profile import StudentProfile


class ProfileService:
    def completeness(self, profile: StudentProfile) -> float:
        dimensions = (
            profile.interests,
            profile.abilities,
            profile.values,
            profile.subjects,
            profile.skills,
            profile.trajectory,
        )
        return fmean(1.0 if dimension else 0.0 for dimension in dimensions)

    def dimension_confidence(self, profile: StudentProfile, dimension: str) -> float:
        values = getattr(profile, dimension)
        if isinstance(values, dict) and values:
            return fmean(float(value) for value in values.values())
        if dimension == "skills" and profile.skills:
            return fmean(skill.confidence for skill in profile.skills)
        return 0.0
