import json
import os
import socket
import time
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter

from orientation.config import versions
from orientation.infrastructure.knowledge.coverage import coverage_for

router = APIRouter(tags=["system"])

_START = time.time()
_DEFAULT_DATA = Path(__file__).resolve().parents[3] / "data" / "knowledge" / "v1"


def _database_status() -> dict[str, object]:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        return {"configured": False, "reachable": None}
    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    started = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=1.5):
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "configured": True,
            "host": host,
            "port": port,
            "reachable": True,
            "latency_ms": latency_ms,
        }
    except OSError:
        return {"configured": True, "host": host, "port": port, "reachable": False}


def _engine_layers() -> list[dict[str, object]]:
    """État réel des couches du moteur, lu dans le registre des modèles."""
    from orientation.engine.stack import RecommendationStack

    return [outcome.to_dict() for outcome in RecommendationStack().report()]


_RAG_CACHE: dict[str, dict[str, object]] = {}


def _rag_status() -> dict[str, object]:
    """Statistiques RAG, mises en cache.

    Construire l'index coûte ~1,5 s : `/system/info` est rappelé à chaque
    chargement de page, on ne le refait pas à chaque fois. Un échec reste
    silencieux — l'interface affiche « indisponible », pas une page cassée.
    """
    cached = _RAG_CACHE.get("payload")
    if cached is not None:
        return dict(cached)
    found: dict[str, object]
    try:
        from orientation.api.routes.recommendations import get_service
        from orientation.config.settings import get_settings
        from orientation.rag.service import build_from_bundle

        found = dict(build_from_bundle(get_service().knowledge(), get_settings()).stats())
    except Exception as error:
        found = {"indexed": False, "error": type(error).__name__}
    _RAG_CACHE["payload"] = found
    return dict(found)


def _knowledge_counts(data_path: Path) -> dict[str, int]:
    """Volumes réellement présents sur disque, pas des nombres écrits en dur."""
    counts: dict[str, int] = {}
    files = (
        ("directions", "directions.json"),
        ("occupations", "occupations.json"),
        ("formations", "formations.json"),
        ("competences", "competences.json"),
    )
    for name, filename in files:
        path = data_path / filename
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        counts[name] = len(payload) if isinstance(payload, list) else 0
    return counts


@router.get("/system/info")
def system_info() -> dict[str, object]:
    data_path = Path(os.environ.get("DATA_PATH", _DEFAULT_DATA))
    knowledge_dirs = sorted(p.name for p in data_path.parent.iterdir()) if data_path.parent.exists() else []
    return {
        "service": "hashcode-profiling engine",
        "code_version": versions.CODE_VERSION,
        "model_version": os.environ.get("OTHELLOO_MODEL_VERSION", versions.MODEL_VERSION),
        "knowledge_version": os.environ.get("OTHELOO_KNOWLEDGE_VERSION", versions.KNOWLEDGE_VERSION),
        "profile_version": versions.PROFILE_VERSION,
        "assessment_version": versions.ASSESSMENT_VERSION,
        "configuration_version": versions.CONFIGURATION_VERSION,
        "feature_schema_version": versions.FEATURE_SCHEMA_VERSION,
        "data_path": str(data_path),
        "knowledge_versions_available": knowledge_dirs,
        "knowledge_counts": _knowledge_counts(data_path),
        "coverage": coverage_for(os.environ.get("OTHELOO_KNOWLEDGE_VERSION", versions.KNOWLEDGE_VERSION)).describe(),
        "engine_layers": _engine_layers(),
        "rag": _rag_status(),
        "uptime_seconds": round(time.time() - _START, 1),
        "database": _database_status(),
    }
