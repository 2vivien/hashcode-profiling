from pathlib import Path

from fastapi import APIRouter

from orientation.infrastructure.knowledge.manifest import load_manifest

router = APIRouter(tags=["knowledge"])
ROOT = Path(__file__).resolve().parents[4] / "data" / "knowledge"


@router.get("/knowledge/{version}")
def get_knowledge(version: str) -> dict[str, object]:
    manifest = load_manifest(ROOT / version)
    return manifest.model_dump()
