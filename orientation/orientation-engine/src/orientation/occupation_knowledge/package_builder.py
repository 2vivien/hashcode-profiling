from __future__ import annotations

import json
from pathlib import Path

from orientation.occupation_knowledge.models import OccupationRecord
from orientation.occupation_knowledge.onet_package import read_onet_zip
from orientation.occupation_knowledge.packages import read_esco_zip


def _merge(esco: OccupationRecord, onet: OccupationRecord) -> OccupationRecord:
    return esco.model_copy(
        update={
            "source": "merged",
            "source_version": f"{esco.source_version}+{onet.source_version}",
            "onet_soc_code": onet.onet_soc_code,
            "esco_uri": esco.esco_uri,
            "essential_skill_ids": esco.essential_skill_ids,
            "optional_skill_ids": esco.optional_skill_ids,
            "riasec": onet.riasec or esco.riasec,
            "abilities": onet.abilities,
            "skills": {**esco.skills, **onet.skills},
            "knowledge": onet.knowledge,
            "work_style": onet.work_style,
            "environment": onet.environment,
            "work_activities": onet.work_activities,
            "job_zone": onet.job_zone,
            "training": onet.training,
            "related_occupation_ids": onet.related_occupation_ids,
            "task_terms": onet.task_terms,
            "provenance": tuple(dict.fromkeys(esco.provenance + onet.provenance + ("exact_title_match",))),
            "evidence_count": esco.evidence_count + onet.evidence_count,
            "data_completeness": min(1.0, (esco.data_completeness + onet.data_completeness) / 2 + 0.15),
        }
    )


def build_catalog(
    *,
    esco_zip: Path,
    onet_zip: Path,
    output: Path,
    language: str = "en",
) -> int:
    esco = read_esco_zip(esco_zip, version="v1.2.1", language=language)
    onet = read_onet_zip(onet_zip, version="31.0")
    onet_by_title = {item.title.casefold().strip(): item for item in onet}

    merged: list[OccupationRecord] = []
    seen_onet: set[str] = set()
    for item in esco:
        counterpart = onet_by_title.get(item.title.casefold().strip())
        if counterpart is not None:
            merged.append(_merge(item, counterpart))
            seen_onet.add(counterpart.occupation_id)
        else:
            merged.append(item)

    # Keep O*NET-only occupations; no fabricated crosswalk is created.
    merged.extend(item for item in onet if item.occupation_id not in seen_onet)

    merged.sort(key=lambda item: item.title.casefold())
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in merged:
            handle.write(json.dumps(record.model_dump(mode="json"), ensure_ascii=False) + "\n")
    return len(merged)
