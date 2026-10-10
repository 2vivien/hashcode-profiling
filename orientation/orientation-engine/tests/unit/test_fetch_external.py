"""Le fetcher doit rester traçable, idempotent et prudent."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import ClassVar

import pytest


def load_fetcher() -> ModuleType:
    """Le fetcher est un script d'outillage, hors paquet : on le charge par chemin."""
    path = Path(__file__).resolve().parents[2] / "scripts" / "fetch_external.py"
    spec = importlib.util.spec_from_file_location("fetch_external", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Les dataclasses du moduleChargé look up sys.modules : il faut l'y inscrire.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


fetcher = load_fetcher()


def test_artifacts_from_flat_downloads() -> None:
    artifacts = fetcher.artifacts_for("onet", {"version": "31.0", "downloads": {"excel": "https://x/db.zip"}})
    assert [item.name for item in artifacts] == ["excel"]
    assert artifacts[0].filename == "db.zip"


def test_artifacts_join_base_url_with_filename() -> None:
    config = {"base_url": "https://host/rome/", "files": {"comp": "rome.xlsx", "bad": "http://evil/x.xlsx"}}
    artifacts = fetcher.artifacts_for("rome", config)
    assert artifacts[0].url == "https://host/rome/rome.xlsx"
    # Un fichier qui est déjà une URL absolue n'est pas re-préfixé.
    assert artifacts[1].url == "http://evil/x.xlsx"


def test_source_without_direct_url_yields_nothing() -> None:
    assert fetcher.artifacts_for("esco", {"version": "1.2.1", "download_page": "https://x"}) == []


def test_service_source_is_reported_not_downloaded(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    fetcher.RAW = tmp_path / "raw"
    handled = fetcher.fetch("esco", {"version": "1.2.1"}, force=False, dry_run=False, timeout=1, pause=0.0)
    assert handled == 0
    assert "service" in capsys.readouterr().out


def test_download_records_provenance_and_is_idempotent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fetcher.RAW = tmp_path / "raw"
    payload = b"contenu-officiel"
    calls: list[str] = []

    class FakeResponse(io.BytesIO):
        headers: ClassVar[dict[str, str]] = {"Content-Type": "application/zip"}

        def geturl(self) -> str:
            return "https://example.test/db.zip"

    def fake_urlopen(request: object, timeout: int | None = None) -> FakeResponse:
        calls.append(str(request.full_url))  # type: ignore[attr-defined]
        return FakeResponse(payload)

    monkeypatch.setattr(fetcher.urllib.request, "urlopen", fake_urlopen)
    config = {"version": "31.0", "license": "CC BY 4.0", "downloads": {"excel": "https://example.test/db.zip"}}

    assert fetcher.fetch("onet", config, force=False, dry_run=False, timeout=5, pause=0.0) == 1
    assert len(calls) == 1

    manifest = json.loads((tmp_path / "raw" / "onet" / "manifest.json").read_text(encoding="utf-8"))
    entry = manifest["artifacts"]["excel"]
    assert entry["bytes"] == len(payload)
    assert entry["license"] == "CC BY 4.0"
    assert len(entry["sha256"]) == 64
    assert entry["downloaded_at"].endswith("+00:00")

    # Second passage : rien à retélécharger.
    assert fetcher.fetch("onet", config, force=False, dry_run=False, timeout=5, pause=0.0) == 1
    assert len(calls) == 1

    # --force force bien le retéléchargement.
    fetcher.fetch("onet", config, force=True, dry_run=False, timeout=5, pause=0.0)
    assert len(calls) == 2


def test_failed_download_leaves_no_partial_archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fetcher.RAW = tmp_path / "raw"

    def boom(request: object, timeout: int | None = None) -> io.BytesIO:
        raise OSError("connexion réinitialisée")

    monkeypatch.setattr(fetcher.urllib.request, "urlopen", boom)
    handled = fetcher.fetch("onet", {"downloads": {"excel": "https://example.test/db.zip"}}, force=False, dry_run=False, timeout=1, pause=0.0)
    assert handled == 0
    assert not (tmp_path / "raw" / "onet" / "db.zip").exists()
    assert not (tmp_path / "raw" / "onet" / "db.zip.part").exists()


def test_shipped_catalog_declares_real_urls() -> None:
    """Le catalogue embarqué doit rester cohérent avec le fetcher."""
    catalog = json.loads((fetcher.CATALOG).read_text(encoding="utf-8"))
    assert catalog["onet"]["downloads"]["excel"].startswith("https://www.onetcenter.org/")
    assert catalog["rome"]["files"]["arborescence_competences"].endswith(".xlsx")
    assert "rejected" in catalog
