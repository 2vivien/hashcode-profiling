import json
from argparse import ArgumentParser
from pathlib import Path

import numpy as np

from orientation.learning.rgcn import RGCNConfig, RGCNModel


def subgraph(
    features: np.ndarray,
    edges: np.ndarray,
    relations: np.ndarray,
    labels: np.ndarray,
    node_ids: list[int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    selected = np.asarray(sorted(set(node_ids)), dtype=np.int64)
    if len(selected) == 0:
        raise ValueError("graph split cannot be empty")
    if np.any(selected < 0) or np.any(selected >= len(features)):
        raise ValueError("graph split contains an invalid node id")
    mapping = {int(node): index for index, node in enumerate(selected)}
    keep = np.asarray(
        [
            int(source) in mapping and int(target) in mapping
            for source, target in edges.T
        ],
        dtype=bool,
    )
    local_edges = edges[:, keep].copy()
    for index in range(local_edges.shape[1]):
        local_edges[0, index] = mapping[int(local_edges[0, index])]
        local_edges[1, index] = mapping[int(local_edges[1, index])]
    return (
        features[selected],
        local_edges,
        relations[keep],
        labels[selected],
    )


def main() -> None:
    parser = ArgumentParser(
        description="Train R-GCN on a leakage-safe inductive graph split.",
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    required = {"node_features", "edges", "relations", "labels", "train_nodes", "validation_nodes"}
    if not required.issubset(payload):
        raise ValueError(f"graph dataset must contain {sorted(required)}")

    features = np.asarray(payload["node_features"], dtype=np.float64)
    edges = np.asarray(payload["edges"], dtype=np.int64)
    relations = np.asarray(payload["relations"], dtype=np.int64)
    labels = np.asarray(payload["labels"], dtype=np.int64)
    train_nodes = [int(node) for node in payload["train_nodes"]]
    validation_nodes = [int(node) for node in payload["validation_nodes"]]

    if set(train_nodes) & set(validation_nodes):
        raise ValueError("graph split leaks nodes across train and validation")
    train_features, train_edges, train_relations, train_labels = subgraph(
        features, edges, relations, labels, train_nodes
    )
    validation_features, validation_edges, validation_relations, validation_labels = subgraph(
        features, edges, relations, labels, validation_nodes
    )

    model = RGCNModel(RGCNConfig())
    model.fit(train_features, train_edges, train_relations, train_labels)
    predictions = model.predict(
        validation_features,
        validation_edges,
        validation_relations,
    )
    predicted_labels = np.argmax(predictions, axis=1)
    accuracy = float(np.mean(predicted_labels == validation_labels))

    parameters = (
        model.relation_weights,
        model.self_weight,
        model.output_weight,
        model.output_bias,
    )
    if any(value is None for value in parameters):
        raise RuntimeError("RGCN training produced no model parameters")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    relation_weights, self_weight, output_weight, output_bias = parameters
    np.savez_compressed(
        args.output,
        relation_weights=relation_weights,
        self_weight=self_weight,
        output_weight=output_weight,
        output_bias=output_bias,
    )
    report = {
        "train_nodes": len(train_nodes),
        "validation_nodes": len(validation_nodes),
        "train_edges": int(train_edges.shape[1]),
        "validation_edges": int(validation_edges.shape[1]),
        "validation_accuracy": accuracy,
        "split": "inductive_node_disjoint",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
