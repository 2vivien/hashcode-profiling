from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path

from orientation.occupation_knowledge.models import OccupationRecord


def read_onet_zip(path: Path, version: str = "31.0") -> list[OccupationRecord]:
    """Read the official O*NET 31.0 tabular archive."""
    with zipfile.ZipFile(path) as archive:
        name = next(
            (item for item in archive.namelist() if item.lower().endswith("occupation data.txt")),
            None,
        )
        if name is None:
            raise ValueError("O*NET archive does not contain Occupation Data.txt")
        with archive.open(name) as raw:
            rows = csv.DictReader(
                io.TextIOWrapper(raw, encoding="utf-8-sig"),
                delimiter="\t",
            )
            records = []
            for row in rows:
                code = row.get("O*NET-SOC Code", "").strip()
                title = row.get("Title", "").strip()
                if not code or not title:
                    continue
                records.append(
                    OccupationRecord(
                        occupation_id=f"onet:{code}",
                        source="onet",
                        source_version=version,
                        title=title,
                        description=row.get("Description", "").strip(),
                        evidence_count=1,
                        data_completeness=0.25,
                    )
                )
    return records
