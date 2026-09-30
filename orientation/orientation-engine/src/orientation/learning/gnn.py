from orientation.learning.rgcn import RGCNConfig, RGCNModel


class GNNBackend:
    """Stable V5 GNN facade backed by the relation-aware R-GCN implementation."""

    def __init__(self, config: RGCNConfig | None = None) -> None:
        self.model = RGCNModel(config)

    def fit(self, node_features, edge_index, relation_types, labels) -> None:
        self.model.fit(node_features, edge_index, relation_types, labels)

    def predict(self, node_features, edge_index, relation_types):
        return self.model.predict(node_features, edge_index, relation_types)
