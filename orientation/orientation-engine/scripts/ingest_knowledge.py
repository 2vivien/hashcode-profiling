from argparse import ArgumentParser
from pathlib import Path
import json
from orientation.knowledge.snapshot import build_snapshot
from orientation.knowledge.sources import CsvKnowledgeSource, JsonKnowledgeSource

def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--json", action="append", default=[])
    parser.add_argument("--csv", action="append", default=[])
    args = parser.parse_args()
    records = []
    for spec in args.json:
        source, path = spec.split("=", 1)
        records.extend(JsonKnowledgeSource(Path(path), source).records())
    for spec in args.csv:
        source, path, id_column, label_column = spec.split("=", 1)
        parts = path.split("=", 1)
        if len(parts) != 2:
            raise ValueError("--csv expects source=path:id_column:label_column")
        file_path, columns = parts
        id_column, label_column = columns.split(":", 1)
        records.extend(CsvKnowledgeSource(Path(file_path), source, id_column, label_column).records())
    snapshot = build_snapshot(args.version, records, args.output)
    print(json.dumps({"version": snapshot.version, "records": len(snapshot.records), "sha256": snapshot.sha256}))

if __name__ == "__main__":
    main()
