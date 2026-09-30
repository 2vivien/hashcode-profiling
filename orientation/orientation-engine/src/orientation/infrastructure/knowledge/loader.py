from pathlib import Path
from orientation.contracts.direction import Direction
from orientation.infrastructure.knowledge.repository import KnowledgeRepository

class KnowledgeLoader:
    def __init__(self, root: Path) -> None:
        self.repository = KnowledgeRepository(root)

    def load_directions(self) -> list[Direction]:
        return self.repository.directions()
