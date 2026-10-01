from __future__ import annotations

import json
from pathlib import Path

from orientation.occupation_knowledge.ingest import (
    merge_records,
    read_esco_occupations,
    read_onet_occupation_data,
)


def build_catalog(
    output: Path,
    esco_occupations: Path | None = None,
    onet_occupation_data: Path | None = None,
) -> int:
    records = []
    if esco_occupations is not None:
        records.extend(read_esco_occupations(esco_occupations))
    if onet_occupation_data is not None:
        records.extend(read_onet_occupation_data(onet_occupation_data))
    if not records:
        raise ValueError("At least one official source file is required")
    merged = merge_records(records)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in merged:
            handle.write(
                json.dumps(record.model_dump(mode="json"), ensure_ascii=False, sort_keys=True)
                + "\n"
            )
    return len(merged)
