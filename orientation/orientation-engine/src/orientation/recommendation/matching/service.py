from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile
from orientation.contracts.scoring import MatchResult
from orientation.domain.skills.matching import SkillMatcher
from orientation.recommendation.matching.vector import VectorMatcher


class MatchingService:
    def __init__(self) -> None:
        self.vector = VectorMatcher()
        self.skills = SkillMatcher()

    def all_matches(self, profile: StudentProfile, direction: Direction) -> dict[str, MatchResult]:
        return {
            "interest": self.vector.match(profile, direction, "interests"),
            "ability": self.vector.match(profile, direction, "abilities"),
            "value": self.vector.match(profile, direction, "values"),
            "subject": self.vector.match(profile, direction, "subjects"),
            "trajectory": self.vector.match(profile, direction, "trajectory"),
            "skill": self.skills.match(profile, direction),
        }
