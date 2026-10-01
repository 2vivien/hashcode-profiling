import json
from argparse import ArgumentParser
from pathlib import Path

import numpy as np

from orientation.learning.calibration import ScoreCalibrator


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--method", choices=("sigmoid", "isotonic"), default="sigmoid")
    args = parser.parse_args()

    rows = [
        json.loads(line)
        for line in args.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    scores = np.asarray([float(row["score"]) for row in rows], dtype=np.float64)
    labels = np.asarray([int(row["label"]) for row in rows], dtype=np.int64)
    calibrator = ScoreCalibrator(args.method)
    report = calibrator.fit(scores, labels)
    evaluation = calibrator.evaluate(scores, labels)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "method": args.method,
                "fit": report.__dict__,
                "evaluation": evaluation.__dict__,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps(evaluation.__dict__))


if __name__ == "__main__":
    main()
