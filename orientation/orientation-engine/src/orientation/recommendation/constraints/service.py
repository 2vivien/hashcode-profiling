from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile

class ConstraintService:
    def evaluate(self, profile: StudentProfile, direction: Direction) -> str:
        if direction.requirements.get("blocked") is True:
            return "fail"
        if profile.constraints.get("location") and direction.accessibility.get("location"):
            left, right = profile.constraints["location"], direction.accessibility["location"]
            if isinstance(left, str) and isinstance(right, str) and left != right:
                return "unknown"
        return "pass"
