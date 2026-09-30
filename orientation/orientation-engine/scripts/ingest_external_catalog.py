from argparse import ArgumentParser
from pathlib import Path
from typing import Iterable

from orientation.infrastructure.knowledge.external_sources import (
    DelimitedConceptReader,
    esco_reader,
    local_reader,
    onet_reader,
)
from orientation.infrastructure.knowledge.external_snapshot import build_external_snapshot


def main() -> None:
    parser = ArgumentParser(description="Build a versioned ESCO/O*NET/Otheloo knowledge snapshot.")
    parser.add_argument("--source", choices=("esco", "onet", "local"), required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--delimiter", default=",")
    parser.add_argument("--local-source", default="othello-local")
    args = parser.parse_args()

    reader: DelimitedConceptReader
    if args.source == "esco":
        reader = esco_reader(args.input)
    elif args.source == "onet":
        reader = onet_reader(args.input)
    else:
        reader = local_reader(args.input, args.local_source)

    digest = build_external_snapshot(args.version, reader.read(args.delimiter), args.output)
    print(f"snapshot={args.output} sha256={digest}")


if __name__ == "__main__":
    main()
