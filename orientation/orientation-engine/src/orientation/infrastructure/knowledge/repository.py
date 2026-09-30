import json
from pathlib import Path

from orientation.contracts.direction import Direction


class KnowledgeRepository:
    def __init__(self, root: Path) -> None:
        self.root = root

    def directions(self) -> list[Direction]:
        payload = json.loads((self.root / "directions.json").read_text(encoding="utf-8"))
        return [Direction.model_validate(item) for item in payload]
