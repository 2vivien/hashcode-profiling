import numpy as np

from orientation.learning.rgcn import RGCNConfig, RGCNModel


class GNNBackend:
    """Stable V5 GNN facade backed by the relation-aware R-GCN implementation."""

    def __init__(self, config: RGCNConfig | None = None) -> None:
        self.model = RGCNModel(config)

    def fit(
        self,
        node_features: np.ndarray,
        edge_index: np.ndarray,
        relation_types: np.ndarray,
        labels: np.ndarray,
    ) -> None:
        self.model.fit(node_features, edge_index, relation_types, labels)

    def predict(
        self,
        node_features: np.ndarray,
        edge_index: np.ndarray,
        relation_types: np.ndarray,
    ) -> np.ndarray:
        return self.model.predict(node_features, edge_index, relation_types)
