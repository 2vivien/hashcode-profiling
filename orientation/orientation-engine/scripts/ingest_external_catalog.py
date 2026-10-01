from argparse import ArgumentParser
from pathlib import Path

from orientation.infrastructure.knowledge.external_snapshot import build_external_snapshot
from orientation.infrastructure.knowledge.external_sources import (
    DelimitedConceptReader,
    esco_reader,
    local_reader,
    onet_reader,
)


def reader_for(source: str, path: Path) -> DelimitedConceptReader:
    if source == "esco":
        return esco_reader(path)
    if source == "onet":
        return onet_reader(path)
    return local_reader(path, "othello-local")


def main() -> None:
    parser = ArgumentParser(description="Build a versioned ESCO/O*NET/Otheloo knowledge snapshot.")
    parser.add_argument("--source", choices=("esco", "onet", "local"), required=True)
    parser.add_argument(
        "--input",
        type=Path,
        action="append",
        required=True,
        help="Official export file; repeat for every ESCO/O*NET table to include.",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--delimiter", default=",")
    args = parser.parse_args()

    concepts = []
    for path in args.input:
        concepts.extend(reader_for(args.source, path).read(args.delimiter))

    digest = build_external_snapshot(args.version, concepts, args.output)
    print(f"snapshot={args.output} sha256={digest}")


if __name__ == "__main__":
    main()
