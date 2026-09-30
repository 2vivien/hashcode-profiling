from abc import ABC, abstractmethod

from orientation.contracts.candidate import Candidate
from orientation.contracts.direction import Direction
from orientation.contracts.profile import StudentProfile


class CandidateGenerator(ABC):
    @abstractmethod
    def generate(self, profile: StudentProfile, directions: list[Direction]) -> list[Candidate]:
        raise NotImplementedError
