import json
from argparse import ArgumentParser
from pathlib import Path

import numpy as np

from orientation.learning.fairness import fairness_report


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()

    rows = [
        json.loads(line)
        for line in args.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    groups = np.asarray([str(row["group"]) for row in rows])
    scores = np.asarray([float(row["score"]) for row in rows], dtype=np.float64)
    labels = np.asarray([int(row["label"]) for row in rows], dtype=np.int64)
    report = fairness_report(groups, scores, labels, args.threshold)
    payload = {
        "groups": [metric.__dict__ for metric in report.groups],
        "demographic_parity_gap": report.demographic_parity_gap,
        "equal_opportunity_gap": report.equal_opportunity_gap,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
