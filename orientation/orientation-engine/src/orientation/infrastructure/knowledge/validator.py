from orientation.contracts.direction import Direction

class KnowledgeValidator:
    def validate(self, directions: list[Direction], expected_version: str = "v1") -> None:
        if not directions:
            raise ValueError("Knowledge snapshot contains no directions")
        ids = [item.direction_id for item in directions]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate directionId")
        for direction in directions:
            if direction.knowledge_version != expected_version:
                raise ValueError(f"Unexpected knowledge version: {direction.knowledge_version}")
