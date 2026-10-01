import json
from argparse import ArgumentParser
from pathlib import Path

import numpy as np

from orientation.learning.rgcn import RGCNConfig, RGCNModel


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))

    features = np.asarray(payload["node_features"], dtype=np.float64)
    edges = np.asarray(payload["edges"], dtype=np.int64)
    relations = np.asarray(payload["relations"], dtype=np.int64)
    labels = np.asarray(payload["labels"], dtype=np.int64)

    model = RGCNModel(RGCNConfig())
    model.fit(features, edges, relations, labels)
    if any(value is None for value in (model.relation_weights, model.self_weight, model.output_weight, model.output_bias)):
        raise RuntimeError("RGCN training produced no model parameters")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    assert model.relation_weights is not None
    assert model.self_weight is not None
    assert model.output_weight is not None
    assert model.output_bias is not None
    np.savez_compressed(
        args.output,
        relation_weights=model.relation_weights,
        self_weight=model.self_weight,
        output_weight=model.output_weight,
        output_bias=model.output_bias,
    )
    print(json.dumps({"nodes": len(features), "relations": int(relations.max()) + 1}))


if __name__ == "__main__":
    main()
