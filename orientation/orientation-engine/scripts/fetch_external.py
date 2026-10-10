"""Téléchargement traçable des artefacts externes (O*NET, ROME, ESCO...).

Le reste de la chaîne d'ingestion (`scripts/ingest_external_catalog.py`) attend
des fichiers déjà présents sur disque. Ce script comble ce trou :

- lit les URL déclarées dans `data/catalog/external_sources.json` ;
- télécharge dans `data/raw/<source>/` ;
- calcule le SHA-256 et journalise la provenance (version, licence, URL, date) ;
- est idempotent : ne retélécharge pas un fichier déjà présent et inchangé.

Aucune dépendance hors stdlib : le runtime de production n'installe pas le
groupe `dev` du moteur.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CATALOG = Path(__file__).resolve().parents[1] / "data" / "catalog" / "external_sources.json"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
USER_AGENT = "hashcode-profiling/1.0 (orientation engine; +https://profiler.otheloo.com)"

# Sources « service » : on suit la page, pas un fichier direct.
SERVICE_SOURCES = {"esco", "esco_onet_crosswalk", "wikidata", "datagouv"}


@dataclass(frozen=True)
class Artifact:
    name: str
    url: str
    expected_format: str = ""

    @property
    def filename(self) -> str:
        return self.url.rsplit("/", 1)[-1].split("?", 1)[0] or self.name


def artifacts_for(name: str, config: dict[str, Any]) -> list[Artifact]:
    """Extrait les URL directes d'une source. Une source sans fichier est ignorée."""
    found: list[Artifact] = []
    for key, url in (config.get("downloads") or {}).items():
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            found.append(Artifact(name=key, url=url))
    base = config.get("base_url")
    for key, filename in (config.get("files") or {}).items():
        if not isinstance(filename, str):
            continue
        # Une valeur déjà absolue est une URL : ne pas la re-préfixer.
        if filename.startswith(("http://", "https://")):
            found.append(Artifact(name=key, url=filename))
        elif isinstance(base, str):
            found.append(Artifact(name=key, url=f"{base.rstrip('/')}/{filename}"))
    return found


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest(directory: Path) -> dict[str, Any]:
    manifest_path = directory / "manifest.json"
    if manifest_path.is_file():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"artifacts": {}}


def download(url: str, target: Path, timeout: int) -> tuple[int, str]:
    """Télécharge dans un fichier temporaire puis renomme : pas d'archive tronquée."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    tmp = target.with_suffix(target.suffix + ".part")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        content_type = response.headers.get("Content-Type", "")
        with tmp.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    tmp.replace(target)
    return target.stat().st_size, f"{content_type} | {final_url}"


def fetch(
    source: str,
    config: dict[str, Any],
    *,
    force: bool,
    dry_run: bool,
    timeout: int,
    pause: float,
) -> int:
    artifacts = artifacts_for(source, config)
    if not artifacts:
        kind = "service" if source in SERVICE_SOURCES else "sans URL directe"
        print(f"[{source}] ignorée : {kind} (suivre la page manuellement)")
        return 0

    directory = RAW / source
    directory.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(directory)
    known: dict[str, Any] = manifest.setdefault("artifacts", {})
    manifest["source_version"] = config.get("version")
    manifest["license"] = config.get("license")
    manifest["verified_on"] = config.get("verified_on")

    handled = 0
    for index, artifact in enumerate(artifacts):
        target = directory / artifact.filename
        previous = known.get(artifact.name)
        if target.is_file() and previous and not force:
            digest = sha256_of(target)
            if digest == previous.get("sha256"):
                print(f"[{source}] {artifact.name} : déjà à jour ({digest[:12]}…)")
                handled += 1
                continue
        if dry_run:
            print(f"[{source}] {artifact.name} : [dry-run] {artifact.url}")
            continue

        try:
            size, info = download(artifact.url, target, timeout)
        except (urllib.error.URLError, OSError) as error:
            print(f"[{source}] {artifact.name} : ÉCHEC {error}")
            continue

        digest = sha256_of(target)
        known[artifact.name] = {
            "file": target.name,
            "url": artifact.url,
            "sha256": digest,
            "bytes": size,
            "content_type": info,
            "license": config.get("license"),
            "version": config.get("version"),
            "downloaded_at": datetime.now(UTC).isoformat(),
        }
        print(f"[{source}] {artifact.name} : {size / 1e6:.1f} Mo  sha256={digest[:12]}…")
        handled += 1
        if index + 1 < len(artifacts):
            time.sleep(pause)  # politesse envers les serveurs d'origine

    (directory / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return handled


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", help="Source à traiter (défaut : toutes).")
    parser.add_argument("--force", action="store_true", help="Retélécharge même si le SHA-256 est identique.")
    parser.add_argument("--dry-run", action="store_true", help="Liste les artefacts sans télécharger.")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--pause", type=float, default=2.0, help="Pause entre deux requêtes (s).")
    args = parser.parse_args()

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    sources = args.source or [name for name in catalog if name not in {"policy", "rejected"}]

    total = 0
    for name in sources:
        config = catalog.get(name)
        if not isinstance(config, dict):
            print(f"[{name}] ignorée : entrée absente du catalogue")
            continue
        total += fetch(
            name,
            config,
            force=args.force,
            dry_run=args.dry_run,
            timeout=args.timeout,
            pause=args.pause,
        )
    print(f"[fetch] {total} artefact(s) disponible(s) sous {RAW}")


if __name__ == "__main__":
    main()
