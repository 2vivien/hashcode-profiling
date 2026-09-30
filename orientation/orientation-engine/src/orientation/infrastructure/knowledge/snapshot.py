from dataclasses import dataclass
from orientation.contracts.direction import Direction

@dataclass(frozen=True)
class KnowledgeSnapshot:
    version: str
    directions: tuple[Direction, ...]
