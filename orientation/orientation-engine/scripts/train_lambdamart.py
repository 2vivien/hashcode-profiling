import json
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

import numpy as np

from orientation.evaluation.ranking import (
    average_precision_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)
from orientation.learning.ranking import LambdaMARTModel


def load_rows(path: Path) -> list[dict[str, object]]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not rows:
        raise ValueError("ranking dataset is empty")
    required = {"student_id", "direction_id", "timestamp", "features", "label"}
    if any(not required.issubset(row) for row in rows):
        raise ValueError(f"every row must contain {sorted(required)}")
    return rows


def grouped_temporal_split(
    rows: list[dict[str, object]],
    validation_fraction: float,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if not 0 < validation_fraction < 0.5:
        raise ValueError("validation_fraction must be in (0, 0.5)")
    latest_by_student: dict[str, datetime] = {}
    for row in rows:
        student = str(row["student_id"])
        timestamp = datetime.fromisoformat(str(row["timestamp"]).replace("Z", "+00:00"))
        latest_by_student[student] = max(latest_by_student.get(student, timestamp), timestamp)
    ordered_students = sorted(latest_by_student, key=latest_by_student.get)
    split = max(1, int(len(ordered_students) * (1.0 - validation_fraction)))
    train_students = set(ordered_students[:split])
    train = [row for row in rows if str(row["student_id"]) in train_students]
    validation = [row for row in rows if str(row["student_id"]) not in train_students]
    if not validation:
        raise ValueError("validation split is empty")
    return train, validation


def matrix(
    rows: list[dict[str, object]],
) -> tuple[np.ndarray, np.ndarray, list[int], list[str], list[str]]:
    feature_names = sorted(dict(rows[0]["features"]).keys())
    ordered = sorted(rows, key=lambda row: (str(row["student_id"]), str(row["timestamp"])))
    x = np.asarray(
        [[float(dict(row["features"])[name]) for name in feature_names] for row in ordered],
        dtype=np.float64,
    )
    y = np.asarray([float(row["label"]) for row in ordered], dtype=np.float64)
    groups: list[int] = []
    query_ids: list[str] = []
    current: str | None = None
    count = 0
    for row in ordered:
        query = str(row["student_id"])
        if current is not None and query != current:
            groups.append(count)
            query_ids.append(current)
            count = 0
        current = query
        count += 1
    if current is not None:
        groups.append(count)
        query_ids.append(current)
    return x, y, groups, feature_names, query_ids


def evaluate_grouped(
    rows: list[dict[str, object]],
    scores: np.ndarray,
    k: int,
) -> dict[str, float]:
    grouped: dict[str, list[tuple[float, float]]] = {}
    ordered = sorted(rows, key=lambda row: (str(row["student_id"]), str(row["timestamp"])))
    for row, score in zip(ordered, scores, strict=True):
        grouped.setdefault(str(row["student_id"]), []).append((float(row["label"]), float(score)))
    values = {"precision": [], "recall": [], "map": [], "ndcg": []}
    for pairs in grouped.values():
        relevance = np.asarray([[label for label, _ in pairs]], dtype=np.float64)
        predictions = np.asarray([[score for _, score in pairs]], dtype=np.float64)
        local_k = min(k, len(pairs))
        values["precision"].append(precision_at_k(relevance, predictions, local_k))
        values["recall"].append(recall_at_k(relevance, predictions, local_k))
        values["map"].append(average_precision_at_k(relevance, predictions, local_k))
        values["ndcg"].append(ndcg_at_k(relevance, predictions, local_k))
    return {f"{name}_at_{k}": float(np.mean(items)) for name, items in values.items()}


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    args = parser.parse_args()

    rows = load_rows(args.input)
    train_rows, validation_rows = grouped_temporal_split(rows, args.validation_fraction)
    x_train, y_train, groups, feature_names, _ = matrix(train_rows)
    x_validation, _, _, _, _ = matrix(validation_rows)

    model = LambdaMARTModel()
    model.fit(x_train, y_train, groups, feature_names)
    validation_scores = model.predict(x_validation)

    metrics = evaluate_grouped(validation_rows, validation_scores, k=5)
    report = {
        "train_rows": len(train_rows),
        "validation_rows": len(validation_rows),
        "features": feature_names,
        "validation_students": len({str(row["student_id"]) for row in validation_rows}),
        **metrics,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    model.save(args.output)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
