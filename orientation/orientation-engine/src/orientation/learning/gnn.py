from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class GraphEmbedding:
    node_id: str
    vector: tuple[float, ...]

class GNNBackend:
    """Explicit V5 contract; no fake neural training is performed without the optional stack and data."""

    def __init__(self) -> None:
        self.trained = False

    def fit(self, node_features: np.ndarray, edge_index: np.ndarray, labels: np.ndarray) -> None:
        try:
            import torch
            import torch_geometric
        except ImportError as exc:
            raise RuntimeError("Install torch and torch-geometric for V5 training") from exc
        _ = (torch, torch_geometric, node_features, edge_index, labels)
        raise NotImplementedError("Select and benchmark a GNN architecture on the Otheloo graph before training")

    def predict(self, node_features: np.ndarray, edge_index: np.ndarray) -> np.ndarray:
        if not self.trained:
            raise RuntimeError("GNN model is not trained")
        return np.zeros(len(node_features), dtype=np.float64)
