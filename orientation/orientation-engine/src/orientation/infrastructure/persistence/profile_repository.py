from orientation.contracts.profile import StudentProfile

class InMemoryProfileRepository:
    def __init__(self) -> None:
        self._items: dict[str,StudentProfile] = {}

    def save(self, profile: StudentProfile) -> StudentProfile:
        self._items[profile.student_id] = profile
        return profile

    def get(self, student_id: str) -> StudentProfile | None:
        return self._items.get(student_id)
