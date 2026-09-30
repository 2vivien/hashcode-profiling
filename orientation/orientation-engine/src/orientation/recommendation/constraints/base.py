from abc import ABC, abstractmethod
from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile

class Constraint(ABC):
    @abstractmethod
    def evaluate(self, profile: StudentProfile, direction: Direction) -> str:
        raise NotImplementedError
