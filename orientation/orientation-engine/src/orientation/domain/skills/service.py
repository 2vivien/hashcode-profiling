from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile
from orientation.domain.skills.matching import SkillMatcher

class SkillService:
    def __init__(self) -> None:
        self.matcher = SkillMatcher()

    def match(self, profile: StudentProfile, direction: Direction):
        return self.matcher.match(profile, direction)
