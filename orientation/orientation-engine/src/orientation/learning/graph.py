from collections import deque
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    relation: str
    weight: float = 1.0


class KnowledgeGraph:
    def __init__(self) -> None:
        self._adjacency: dict[str, list[GraphEdge]] = {}

    def add_edges(self, edges: Iterable[GraphEdge]) -> None:
        for edge in edges:
            self._adjacency.setdefault(edge.source, []).append(edge)
            self._adjacency.setdefault(edge.target, [])

    def related(self, node_id: str, depth: int = 2) -> set[str]:
        if node_id not in self._adjacency or depth < 0:
            return set()
        visited = {node_id}
        queue: deque[tuple[str, int]] = deque([(node_id, 0)])
        while queue:
            current, distance = queue.popleft()
            if distance == depth:
                continue
            for edge in self._adjacency.get(current, []):
                if edge.target not in visited:
                    visited.add(edge.target)
                    queue.append((edge.target, distance + 1))
        return visited

    def score(self, source: str, target: str) -> float:
        if source == target:
            return 1.0
        if source not in self._adjacency or target not in self._adjacency:
            return 0.0
        queue: deque[tuple[str, int]] = deque([(source, 0)])
        visited = {source}
        while queue:
            current, distance = queue.popleft()
            for edge in self._adjacency.get(current, []):
                if edge.target == target:
                    return 1.0 / (2.0 + distance)
                if edge.target not in visited:
                    visited.add(edge.target)
                    queue.append((edge.target, distance + 1))
        return 0.0
