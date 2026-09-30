from dataclasses import dataclass
from typing import Iterable
import networkx as nx

@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    relation: str
    weight: float = 1.0

class KnowledgeGraph:
    def __init__(self) -> None:
        self.graph = nx.MultiDiGraph()

    def add_edges(self, edges: Iterable[GraphEdge]) -> None:
        for edge in edges:
            self.graph.add_edge(edge.source, edge.target, relation=edge.relation, weight=edge.weight)

    def related(self, node_id: str, depth: int = 2) -> set[str]:
        if node_id not in self.graph:
            return set()
        return set(nx.single_source_shortest_path_length(self.graph, node_id, cutoff=depth))

    def score(self, source: str, target: str) -> float:
        if source == target:
            return 1.0
        try:
            distance = nx.shortest_path_length(self.graph, source, target)
        except nx.NetworkXNoPath:
            return 0.0
        return 1.0 / (1.0 + float(distance))
