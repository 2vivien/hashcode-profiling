from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RGCNConfig:
    hidden_dim: int = 32
    epochs: int = 200
    learning_rate: float = 0.01
    l2: float = 1e-4


class RGCNModel:
    """One-layer R-GCN node classifier following relation-specific message passing."""

    def __init__(self, config: RGCNConfig | None = None, seed: int = 42) -> None:
        self.config = config or RGCNConfig()
        if self.config.hidden_dim <= 0 or self.config.epochs <= 0:
            raise ValueError("hidden_dim and epochs must be positive")
        if self.config.learning_rate <= 0 or self.config.l2 < 0:
            raise ValueError("learning_rate must be positive and l2 cannot be negative")
        self.seed = seed
        self.relation_weights: np.ndarray | None = None
        self.self_weight: np.ndarray | None = None
        self.output_weight: np.ndarray | None = None
        self.output_bias: np.ndarray | None = None

    @staticmethod
    def _softmax(logits: np.ndarray) -> np.ndarray:
        shifted = logits - np.max(logits, axis=1, keepdims=True)
        exponentials = np.asarray(
            np.exp(np.clip(shifted, -40.0, 40.0)),
            dtype=np.float64,
        )
        return np.asarray(
            exponentials / np.sum(exponentials, axis=1, keepdims=True),
            dtype=np.float64,
        )

    @staticmethod
    def _validate(
        features: np.ndarray,
        edges: np.ndarray,
        relations: np.ndarray,
        labels: np.ndarray,
    ) -> None:
        if features.ndim != 2 or edges.ndim != 2 or edges.shape[0] != 2:
            raise ValueError("features must be [nodes, features] and edges must be [2, edges]")
        if not np.all(np.isfinite(features)):
            raise ValueError("graph features must contain only finite values")
        if len(relations) != edges.shape[1] or len(labels) != len(features):
            raise ValueError("graph arrays must align")
        if len(relations) and np.min(relations) < 0:
            raise ValueError("relation ids must be non-negative")
        if len(labels) and np.min(labels) < 0:
            raise ValueError("labels must be non-negative")
        if edges.shape[1] and (
            np.max(edges) >= len(features) or np.min(edges) < 0
        ):
            raise ValueError("edge node ids are outside the feature matrix")

    def _aggregate(
        self,
        features: np.ndarray,
        edges: np.ndarray,
        relations: np.ndarray,
        weights: np.ndarray,
        self_weight: np.ndarray,
    ) -> np.ndarray:
        hidden = np.asarray(features @ self_weight, dtype=np.float64)
        for relation in range(weights.shape[0]):
            mask = relations == relation
            relation_edges = edges[:, mask]
            if relation_edges.shape[1] == 0:
                continue
            counts = np.bincount(
                relation_edges[1],
                minlength=len(features),
            ).astype(np.float64)
            for edge_index in range(relation_edges.shape[1]):
                source = int(relation_edges[0, edge_index])
                target = int(relation_edges[1, edge_index])
                hidden[target] += features[source] @ weights[relation] / max(
                    counts[target], 1.0
                )
        return np.asarray(hidden, dtype=np.float64)

    def fit(
        self,
        features: np.ndarray,
        edges: np.ndarray,
        relations: np.ndarray,
        labels: np.ndarray,
    ) -> None:
        self._validate(features, edges, relations, labels)
        if len(features) == 0:
            raise ValueError("graph cannot be empty")
        rng = np.random.default_rng(self.seed)
        input_dim = features.shape[1]
        relation_count = int(np.max(relations)) + 1 if len(relations) else 1
        class_count = int(np.max(labels)) + 1
        if class_count < 2:
            raise ValueError("RGCN classification requires at least two classes")
        scale = 1.0 / np.sqrt(max(input_dim, 1))
        relation_weights = rng.normal(
            0.0,
            scale,
            (relation_count, input_dim, self.config.hidden_dim),
        )
        self_weight = rng.normal(0.0, scale, (input_dim, self.config.hidden_dim))
        output_weight = rng.normal(
            0.0,
            scale,
            (self.config.hidden_dim, class_count),
        )
        output_bias = np.zeros(class_count, dtype=np.float64)

        for _ in range(self.config.epochs):
            pre_activation = self._aggregate(
                features, edges, relations, relation_weights, self_weight
            )
            hidden = np.maximum(pre_activation, 0.0)
            probabilities = self._softmax(hidden @ output_weight + output_bias)
            gradient_logits = probabilities.copy()
            gradient_logits[np.arange(len(labels)), labels] -= 1.0
            gradient_logits /= len(labels)

            gradient_output = hidden.T @ gradient_logits + self.config.l2 * output_weight
            gradient_bias = np.sum(gradient_logits, axis=0)
            gradient_hidden = gradient_logits @ output_weight.T
            gradient_pre = gradient_hidden * (pre_activation > 0)

            gradient_self = features.T @ gradient_pre + self.config.l2 * self_weight
            gradient_relations = np.zeros_like(relation_weights)
            for relation in range(relation_count):
                mask = relations == relation
                relation_edges = edges[:, mask]
                if relation_edges.shape[1] == 0:
                    continue
                counts = np.bincount(
                    relation_edges[1],
                    minlength=len(features),
                ).astype(np.float64)
                for edge_index in range(relation_edges.shape[1]):
                    source = int(relation_edges[0, edge_index])
                    target = int(relation_edges[1, edge_index])
                    gradient_relations[relation] += np.outer(
                        features[source], gradient_pre[target]
                    ) / max(counts[target], 1.0)
                gradient_relations[relation] += (
                    self.config.l2 * relation_weights[relation]
                )

            relation_weights -= self.config.learning_rate * gradient_relations
            self_weight -= self.config.learning_rate * gradient_self
            output_weight -= self.config.learning_rate * gradient_output
            output_bias -= self.config.learning_rate * gradient_bias

        self.relation_weights = relation_weights
        self.self_weight = self_weight
        self.output_weight = output_weight
        self.output_bias = output_bias

    def predict(
        self,
        features: np.ndarray,
        edges: np.ndarray,
        relations: np.ndarray,
    ) -> np.ndarray:
        if any(
            value is None
            for value in (
                self.relation_weights,
                self.self_weight,
                self.output_weight,
                self.output_bias,
            )
        ):
            raise RuntimeError("RGCN model is not trained")
        relation_weights = self.relation_weights
        self_weight = self.self_weight
        output_weight = self.output_weight
        output_bias = self.output_bias
        assert relation_weights is not None
        assert self_weight is not None
        assert output_weight is not None
        assert output_bias is not None
        if features.ndim != 2 or features.shape[1] != self_weight.shape[0]:
            raise ValueError("prediction features have the wrong shape")
        if edges.ndim != 2 or edges.shape[0] != 2:
            raise ValueError("prediction edges must be [2, edges]")
        if len(relations) != edges.shape[1]:
            raise ValueError("prediction relations must align with edges")
        if len(relations) and np.max(relations) >= relation_weights.shape[0]:
            raise ValueError("prediction relation id exceeds trained relation schema")
        hidden = np.maximum(
            self._aggregate(features, edges, relations, relation_weights, self_weight),
            0.0,
        )
        return self._softmax(hidden @ output_weight + output_bias)
