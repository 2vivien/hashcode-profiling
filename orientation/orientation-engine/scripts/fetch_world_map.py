#!/usr/bin/env python3
"""Télécharge les contours du monde (Natural Earth 110 m, domaine public).

Sans ce fichier, `map_professions.py` ne peut pas dessiner de vraie carte — il
ne dessinerait qu'une grille de points, ce qui ne veut rien dire géographiquement.

Le fichier est volumineux et externe : il reste hors du dépôt (voir .gitignore),
seul son manifeste de provenance est versionné.

Usage : python3 scripts/fetch_world_map.py
"""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

SOURCE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
LICENSE = "Public domain (Natural Earth)"
USER_AGENT = "hashcode-profiling/1.0 (orientation engine; +https://profiler.otheloo.com)"

RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "geography"
TARGET = RAW / "ne_110m_admin_0_countries.geojson"
MANIFEST = RAW / "manifest.json"


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)

    known: dict[str, object] = {}
    if MANIFEST.is_file():
        try:
            known = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            known = {}

    if TARGET.is_file() and known.get("sha256"):
        digest = hashlib.sha256(TARGET.read_bytes()).hexdigest()
        if digest == known["sha256"]:
            print(f"[geo] déjà à jour ({digest[:12]}…, {TARGET.stat().st_size // 1024} Ko)")
            return 0

    request = urllib.request.Request(SOURCE, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = response.read()
    except (urllib.error.URLError, OSError) as error:
        print(f"[geo] téléchargement impossible : {error}")
        return 1

    TARGET.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    manifest = {
        "geography": {
            "file": TARGET.name,
            "url": SOURCE,
            "sha256": digest,
            "bytes": len(payload),
            "license": LICENSE,
            "resolution": "110m (1 : 110 000 000)",
            "downloaded_at": datetime.now(UTC).isoformat(),
        }
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[geo] {len(payload) // 1024} Ko téléchargés · sha256={digest[:12]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
