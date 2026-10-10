from orientation.contracts.profile import StudentProfile


class InMemoryProfileRepository:
    """Cache mémoire : dernier profil + historique des versions."""

    def __init__(self) -> None:
        self._items: dict[str, StudentProfile] = {}
        self._history: dict[str, list[StudentProfile]] = {}

    def save(self, profile: StudentProfile) -> StudentProfile:
        self._items[profile.student_id] = profile
        self._history.setdefault(profile.student_id, []).append(profile)
        return profile

    def get(self, student_id: str) -> StudentProfile | None:
        return self._items.get(student_id)

    def history(self, student_id: str) -> list[StudentProfile]:
        return list(self._history.get(student_id, []))
