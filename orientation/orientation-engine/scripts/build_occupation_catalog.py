from __future__ import annotations

import argparse
from pathlib import Path

from orientation.occupation_knowledge.package_builder import build_catalog


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an Otheloo occupation catalog from official archives.")
    parser.add_argument("--esco-zip", type=Path, required=True)
    parser.add_argument("--onet-zip", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--language", default="en", choices=("en", "fr"))
    args = parser.parse_args()
    count = build_catalog(
        esco_zip=args.esco_zip,
        onet_zip=args.onet_zip,
        output=args.output,
        language=args.language,
    )
    print(f"occupation_catalog_records={count}")


if __name__ == "__main__":
    main()