from argparse import ArgumentParser
from pathlib import Path
import json


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    records = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("mapping file must contain an array")
    required = {"source_id", "target_id", "relation", "confidence", "source", "review_status", "version"}
    for index, record in enumerate(records):
        if not required.issubset(record):
            raise ValueError(f"mapping {index} is missing required fields")
        if not 0 <= float(record["confidence"]) <= 1:
            raise ValueError(f"mapping {index} has invalid confidence")
        if record["review_status"] == "reviewed" and not record.get("reviewer"):
            raise ValueError(f"reviewed mapping {index} requires reviewer")
    print(f"valid_mappings={len(records)}")


if __name__ == "__main__":
    main()
