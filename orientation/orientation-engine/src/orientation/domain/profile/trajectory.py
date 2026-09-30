from orientation.contracts.profile import StudentProfile


def trajectory_dimensions(profile: StudentProfile) -> dict[str, float]:
    return dict(profile.trajectory)
