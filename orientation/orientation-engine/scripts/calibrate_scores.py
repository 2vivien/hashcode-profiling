import json
from argparse import ArgumentParser
from pathlib import Path

import numpy as np

from orientation.learning.calibration import ScoreCalibrator


def load_scores(path: Path) -> tuple[np.ndarray, np.ndarray]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError(f"calibration dataset is empty: {path}")
    scores = np.asarray([float(row["score"]) for row in rows], dtype=np.float64)
    labels = np.asarray([int(row["label"]) for row in rows], dtype=np.int64)
    return scores, labels


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--fit-input", type=Path, required=True)
    parser.add_argument("--evaluation-input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--method", choices=("sigmoid", "isotonic"), default="sigmoid")
    args = parser.parse_args()

    fit_scores, fit_labels = load_scores(args.fit_input)
    evaluation_scores, evaluation_labels = load_scores(args.evaluation_input)

    calibrator = ScoreCalibrator(args.method)
    fit_report = calibrator.fit(fit_scores, fit_labels)
    evaluation_report = calibrator.evaluate(evaluation_scores, evaluation_labels)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "method": args.method,
                "fit_sample_count": fit_report.sample_count,
                "evaluation": evaluation_report.__dict__,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps(evaluation_report.__dict__))


if __name__ == "__main__":
    main()
