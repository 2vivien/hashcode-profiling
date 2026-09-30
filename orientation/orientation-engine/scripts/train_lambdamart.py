from argparse import ArgumentParser
from pathlib import Path
import json
import numpy as np
from orientation.learning.ranking import LambdaMARTModel

def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError("ranking dataset is empty")
    feature_names = sorted(rows[0]["features"])
    groups = []
    X_rows = []
    y_rows = []
    current = None
    count = 0
    for row in rows:
        query = row["student_id"]
        if current is not None and query != current:
            groups.append(count)
            count = 0
        current = query
        X_rows.append([float(row["features"][name]) for name in feature_names])
        y_rows.append(float(row["label"]))
        count += 1
    groups.append(count)
    model = LambdaMARTModel()
    model.fit(np.asarray(X_rows, dtype=np.float64), np.asarray(y_rows, dtype=np.float64),
              groups, feature_names)
    model.save(args.output)
    print(json.dumps({"queries": len(groups), "rows": len(rows), "features": feature_names}))

if __name__ == "__main__":
    main()
