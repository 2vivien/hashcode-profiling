import os
import socket
import time
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter

from orientation.config import versions

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


@router.get("/system/info")
def system_info() -> dict[str, object]:
    data_path = Path(os.environ.get("DATA_PATH", _DEFAULT_DATA))
    knowledge_dirs = (
        sorted(p.name for p in data_path.parent.iterdir()) if data_path.parent.exists() else []
    )
    return {
        "service": "hashcode-profiling engine",
        "code_version": versions.CODE_VERSION,
        "model_version": os.environ.get("OTHELLOO_MODEL_VERSION", versions.MODEL_VERSION),
        "knowledge_version": os.environ.get(
            "OTHELLOO_KNOWLEDGE_VERSION", versions.KNOWLEDGE_VERSION
        ),
        "profile_version": versions.PROFILE_VERSION,
        "assessment_version": versions.ASSESSMENT_VERSION,
        "configuration_version": versions.CONFIGURATION_VERSION,
        "feature_schema_version": versions.FEATURE_SCHEMA_VERSION,
        "data_path": str(data_path),
        "knowledge_versions_available": knowledge_dirs,
        "uptime_seconds": round(time.time() - _START, 1),
        "database": _database_status(),
    }
