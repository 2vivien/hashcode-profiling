from orientation.contracts.profile import StudentProfile


def profile_completeness(profile: StudentProfile) -> float:
    return (
        sum(
            bool(getattr(profile, field))
            for field in (
                "interests", "abilities", "values", "subjects", "skills", "trajectory"
            )
        )
        / 6
    )
