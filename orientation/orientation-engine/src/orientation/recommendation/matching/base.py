from abc import ABC, abstractmethod
from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile
from orientation.contracts.scoring import MatchResult

class Matcher(ABC):
    @abstractmethod
    def match(self, profile: StudentProfile, direction: Direction) -> MatchResult:
        raise NotImplementedError
