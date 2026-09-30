from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
import json

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


def matrix(rows: list[dict[str, object]]) -> tuple[np.ndarray, np.ndarray, list[int], list[str], list[str]]:
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
    x_validation, y_validation, _, _, validation_queries = matrix(validation_rows)

    model = LambdaMARTModel()
    model.fit(x_train, y_train, groups, feature_names)
    validation_scores = model.predict(x_validation)

    query_order = sorted(validation_queries)
    validation_ordered = sorted(
        validation_rows,
        key=lambda row: (str(row["student_id"]), str(row["timestamp"])),
    )
    query_to_rows = {query: [] for query in query_order}
    for row, score in zip(validation_ordered, validation_scores, strict=True):
        query_to_rows[str(row["student_id"])].append((float(row["label"]), float(score)))
    relevance = np.asarray([row for query in query_order for row, _ in query_to_rows[query]], dtype=np.float64)
    scores = np.asarray([score for query in query_order for _, score in query_to_rows[query]], dtype=np.float64)
    sizes = [len(query_to_rows[query]) for query in query_order]
    max_k = min(5, max(sizes))
    offsets = np.cumsum([0, *sizes])
    relevance_matrix = np.zeros((len(sizes), max(sizes)))
    score_matrix = np.full_like(relevance_matrix, -np.inf)
    for index, (start, end) in enumerate(zip(offsets[:-1], offsets[1:], strict=True)):
        relevance_matrix[index, : end - start] = relevance[start:end]
        score_matrix[index, : end - start] = scores[start:end]

    report = {
        "train_rows": len(train_rows),
        "validation_rows": len(validation_rows),
        "features": feature_names,
        "precision_at_5": precision_at_k(relevance_matrix, score_matrix, k=max_k),
        "recall_at_5": recall_at_k(relevance_matrix, score_matrix, k=max_k),
        "map_at_5": average_precision_at_k(relevance_matrix, score_matrix, k=max_k),
        "ndcg_at_5": ndcg_at_k(relevance_matrix, score_matrix, k=max_k),
        "validation_students": len(query_order),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    model.save(args.output)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
