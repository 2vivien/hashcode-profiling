import json
from pathlib import Path

from orientation.infrastructure.knowledge.external_snapshot import build_external_snapshot
from orientation.infrastructure.knowledge.external_sources import esco_reader, onet_reader


def test_esco_export_reader_and_snapshot(tmp_path: Path) -> None:
    source = tmp_path / "occupations.csv"
    source.write_text(
        "conceptUri,preferredLabel,conceptType\nesco:occupation:1,Software developer,Occupation\n",
        encoding="utf-8",
    )
    output = tmp_path / "snapshot.json"
    digest = build_external_snapshot("esco-v1.2.1", esco_reader(source).read(), output)
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["sha256"] == digest
    assert payload["records"][0]["external_id"] == "esco:occupation:1"


def test_onet_skill_export_reader(tmp_path: Path) -> None:
    source = tmp_path / "Skills.csv"
    source.write_text(
        "Element ID,Element Name\n2.A.1.a,Reading Comprehension\n",
        encoding="utf-8",
    )
    records = list(onet_reader(source).read())
    assert len(records) == 1
    assert records[0].external_id == "2.A.1.a"
    assert records[0].label == "Reading Comprehension"
