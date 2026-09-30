import hashlib
import json
from collections.abc import Iterable
from dataclasses import asdict
from datetime import date
from pathlib import Path

from orientation.infrastructure.knowledge.external_sources import ExternalConcept


def build_external_snapshot(
    version: str,
    concepts: Iterable[ExternalConcept],
    output: Path,
) -> str:
    records = [
        asdict(concept)
        for concept in sorted(
            concepts,
            key=lambda item: (item.source, item.external_id, item.concept_type),
        )
    ]
    raw = json.dumps(
        records,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    digest = hashlib.sha256(raw).hexdigest()
    payload = {
        "version": version,
        "created_at": date.today().isoformat(),
        "sha256": digest,
        "records": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return digest
