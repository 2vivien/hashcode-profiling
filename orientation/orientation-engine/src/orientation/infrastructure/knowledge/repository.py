import json
from pathlib import Path

from orientation.contracts.direction import Direction
from orientation.contracts.formation import Formation
from orientation.occupation_knowledge.models import OccupationRecord


class KnowledgeRepository:
    def __init__(self, root: Path) -> None:
        self.root = root

    def directions(self) -> list[Direction]:
        payload = json.loads((self.root / "directions.json").read_text(encoding="utf-8"))
        return [Direction.model_validate(item) for item in payload]

    def occupations(self) -> list[OccupationRecord]:
        path = self.root / "occupations.json"
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [OccupationRecord.model_validate(item) for item in payload]

    def formations(self) -> list[Formation]:
        path = self.root / "formations.json"
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        return [Formation.model_validate(item) for item in payload]
