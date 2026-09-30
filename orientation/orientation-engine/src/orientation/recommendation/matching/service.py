from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile
from orientation.domain.skills.matching import SkillMatcher
from orientation.recommendation.matching.vector import VectorMatcher

class MatchingService:
    def __init__(self) -> None:
        self.vector = VectorMatcher()
        self.skills = SkillMatcher()

    def all_matches(self, profile: StudentProfile, direction: Direction) -> dict[str, object]:
        return {dimension: self.vector.match(profile,direction,dimension) for dimension in ("interests","abilities","values","subjects","trajectory")} | {"skill": self.skills.match(profile,direction)}
