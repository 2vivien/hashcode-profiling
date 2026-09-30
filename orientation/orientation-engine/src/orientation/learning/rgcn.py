from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class RGCNConfig:
    hidden_dim: int = 64
    epochs: int = 100
    learning_rate: float = 0.01

class RGCNModel:
    """Minimal relation-aware message-passing model with an explicit train/predict lifecycle."""

    def __init__(self, config: RGCNConfig | None = None) -> None:
        self.config = config or RGCNConfig()
        self.model: object | None = None

    def fit(self, features: np.ndarray, edges: np.ndarray, relations: np.ndarray,
            labels: np.ndarray) -> None:
        try:
            import torch
            import torch.nn as nn
        except ImportError as exc:
            raise RuntimeError("Install torch for RGCN training") from exc
        if edges.shape[0] != 2 or len(relations) != edges.shape[1]:
            raise ValueError("edges and relations must align")
        relation_count = int(relations.max()) + 1 if len(relations) else 1
        x = torch.tensor(features, dtype=torch.float32)
        edge_index = torch.tensor(edges, dtype=torch.long)
        rel = torch.tensor(relations, dtype=torch.long)
        y = torch.tensor(labels, dtype=torch.long)

        class Net(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.weights = nn.Parameter(torch.randn(relation_count, features.shape[1],
                                                         self.config.hidden_dim) * 0.02)
                self.out = nn.Linear(self.config.hidden_dim, int(y.max().item()) + 1)

            def forward(self, node_features: object) -> object:
                h = torch.zeros((features.shape[0], self.config.hidden_dim))
                for edge in range(edge_index.shape[1]):
                    src = int(edge_index[0, edge])
                    dst = int(edge_index[1, edge])
                    h[dst] = h[dst] + node_features[src] @ self.weights[rel[edge]]
                h = torch.relu(h)
                return self.out(h)

        net = Net()
        optimizer = torch.optim.Adam(net.parameters(), lr=self.config.learning_rate)
        loss_fn = nn.CrossEntropyLoss()
        for _ in range(self.config.epochs):
            optimizer.zero_grad()
            loss = loss_fn(net(x), y)
            loss.backward()
            optimizer.step()
        self.model = net

    def predict(self, features: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("RGCN model is not trained")
        import torch
        with torch.no_grad():
            logits = self.model(torch.tensor(features, dtype=torch.float32))
        return torch.softmax(logits, dim=-1).numpy()
