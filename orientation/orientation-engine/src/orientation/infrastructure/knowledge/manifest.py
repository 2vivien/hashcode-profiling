import hashlib
import json
from pathlib import Path

from pydantic import BaseModel, Field


class KnowledgeManifest(BaseModel):
    version: str
    source: str
    date: str
    directions: int
    sha256: str
    item_counts: dict[str, int] = Field(default_factory=dict)
    transformation_rules: list[str] = Field(default_factory=list)


def load_manifest(root: Path) -> KnowledgeManifest:
    raw = (root / "manifest.json").read_text(encoding="utf-8")
    data = json.loads(raw)
    content = (root / "directions.json").read_bytes()
    computed_hash = hashlib.sha256(content).hexdigest()
    declared_hash = str(data.get("sha256", ""))
    if declared_hash.startswith("sha256:") and declared_hash != "sha256:directions.json":
        declared_hash = declared_hash.removeprefix("sha256:")
    if declared_hash not in {"", "sha256:directions.json", computed_hash}:
        raise ValueError("knowledge_hash_mismatch")
    data["sha256"] = computed_hash
    return KnowledgeManifest.model_validate(data)
