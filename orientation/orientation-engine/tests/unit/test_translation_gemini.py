"""Le traducteur ne doit jamais publier une traduction douteuse ni perdre la source."""

from __future__ import annotations

import io
import json
import urllib.error
from pathlib import Path
from typing import ClassVar

import pytest

from orientation.infrastructure.translation.base import (
    TranslationCache,
    TranslationSettings,
    TranslationUnavailable,
    parse_translations,
    strip_fence,
)
from orientation.infrastructure.translation.gemini import GeminiTranslator
from orientation.infrastructure.translation.groq import GroqTranslator
from orientation.infrastructure.translation.service import TranslationService


def settings(tmp_path: Path, **overrides: object) -> TranslationSettings:
    base = {
        "api_key": "test-key",
        "model": "gemini-2.5-flash",
        "cache_path": tmp_path / "cache.json",
    }
    base.update(overrides)
    return TranslationSettings(**base)  # type: ignore[arg-type]


def _response(payload: dict[str, object]) -> io.BytesIO:
    body = json.dumps({"candidates": [{"content": {"parts": [{"text": json.dumps(payload)}]}}]})
    stream = io.BytesIO(body.encode())
    stream.headers = {}  # type: ignore[attr-defined]
    return stream


class FakeUrlopen:
    """Remplace urlopen et journalise les en-têtes, pour vérifier qu'aucune clé ne fuit."""

    calls: ClassVar[list[dict[str, str]]] = []

    def __init__(self, text: str | None = None, error: Exception | None = None) -> None:
        self.text = text
        self.error = error

    def __call__(self, request: object, timeout: int | None = None) -> io.BytesIO:
        self.calls.append(dict(request.headers))  # type: ignore[attr-defined]
        if self.error is not None:
            raise self.error
        return _response({"0": self.text or ""})


def test_cache_key_is_stable_and_target_specific() -> None:
    translator_a = GeminiTranslator(settings(Path("/tmp/does-not-matter")))
    translator_b = GeminiTranslator(settings(Path("/tmp/does-not-matter"), target_language="fr"))
    translator_en = GeminiTranslator(settings(Path("/tmp/does-not-matter"), target_language="en"))
    assert translator_a.cache.get("x") is None
    assert translator_a.settings.target_language == "fr"
    assert translator_b.settings.target_language == "fr"
    assert translator_en.settings.target_language == "en"


def test_needs_translation_skips_short_and_pure_symbols() -> None:
    translator = GeminiTranslator(settings(Path("/tmp/none"), api_key=""))
    assert translator.needs_translation("Data analyst")
    assert not translator.needs_translation("")
    assert not translator.needs_translation("A")


def test_strip_fence_removes_markdown_wrapper() -> None:
    assert strip_fence('```json\n{"0": "a"}\n```') == '{"0": "a"}'
    assert strip_fence('{"0": "a"}') == '{"0": "a"}'


def test_disabled_translator_keeps_source_texts(tmp_path: Path) -> None:
    translator = GeminiTranslator(settings(tmp_path, api_key=""))
    assert not translator.enabled
    result = translator.translate_safe(["Data analyst", "Registered nurse"])
    assert result == {"Data analyst": "Data analyst", "Registered nurse": "Registered nurse"}


def test_failed_call_falls_back_to_source(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Une API injoignable ne doit pas faire échouer l'ingestion."""
    from orientation.infrastructure.translation import gemini

    monkeypatch.setattr(
        gemini.urllib.request,
        "urlopen",
        FakeUrlopen(error=urllib.error.URLError("réseau indisponible")),
    )
    monkeypatch.setattr(gemini.time, "sleep", lambda _: None)
    translator = GeminiTranslator(settings(tmp_path))
    with pytest.raises(TranslationUnavailable):
        translator.translate(["Data analyst"])
    assert translator.translate_safe(["Data analyst"]) == {"Data analyst": "Data analyst"}


def test_api_key_travels_in_header_not_in_url(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from orientation.infrastructure.translation import gemini

    FakeUrlopen.calls = []
    monkeypatch.setattr(gemini.urllib.request, "urlopen", FakeUrlopen(text="analyste de données"))
    monkeypatch.setattr(gemini.time, "sleep", lambda _: None)
    translator = GeminiTranslator(settings(tmp_path))
    result = translator.translate(["Data analyst"])

    assert result["Data analyst"] == "analyste de données"
    assert FakeUrlopen.calls, "l'API n'a pas été appelée"
    assert FakeUrlopen.calls[0].get("X-goog-api-key") == "test-key"
    assert FakeUrlopen.calls[0].get("url", "") == ""


def test_cache_avoids_second_paywall_call(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from orientation.infrastructure.translation import gemini

    FakeUrlopen.calls = []
    monkeypatch.setattr(gemini.urllib.request, "urlopen", FakeUrlopen(text="analyste de données"))
    monkeypatch.setattr(gemini.time, "sleep", lambda _: None)
    translator = GeminiTranslator(settings(tmp_path))

    first = translator.translate(["Data analyst"])
    calls_after_first = len(FakeUrlopen.calls)
    second = translator.translate(["Data analyst"])

    assert first == second == {"Data analyst": "analyste de données"}
    assert calls_after_first == 1
    assert len(FakeUrlopen.calls) == calls_after_first  # deuxième appel servi par le cache


def test_cache_file_is_written_for_audit(tmp_path: Path) -> None:
    cache_path = tmp_path / "nested" / "cache.json"
    translator = GeminiTranslator(settings(tmp_path, cache_path=cache_path))
    translator.cache.put("abc", "valeur")
    assert json.loads(cache_path.read_text(encoding="utf-8")) == {"abc": "valeur"}


def test_parse_translations_refuses_incomplete_response() -> None:
    """Une réponse à moitié traduite doit être refusée, pas fusionnée."""
    with pytest.raises(TranslationUnavailable):
        parse_translations('{"0": "infirmier"}', ["Registered nurse", "Computer network administrator"])
    assert parse_translations('{"0": "infirmier", "1": "administrateur réseau"}', ["a", "b"]) == {
        "a": "infirmier",
        "b": "administrateur réseau",
    }


def test_parse_translations_rejects_non_json() -> None:
    with pytest.raises(TranslationUnavailable):
        parse_translations("Voici vos traductions : infirmier", ["Registered nurse"])


def test_service_falls_back_to_second_provider(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Gemini épuisé (429) ne doit pas faire perdre la traduction : Groq prend le relais."""
    from orientation.infrastructure.translation import gemini

    monkeypatch.setattr(
        gemini.urllib.request,
        "urlopen",
        FakeUrlopen(error=urllib.error.HTTPError("url", 429, "rate limited", {}, None)),  # type: ignore[arg-type]
    )
    monkeypatch.setattr(gemini.time, "sleep", lambda _: None)

    cache = TranslationCache(tmp_path / "shared.json")
    primary = GeminiTranslator(TranslationSettings(api_key="k", cache_path=tmp_path / "shared.json"), cache=cache)
    secondary = GroqTranslator(TranslationSettings(api_key="k2", model="qwen/qwen3.8-27b"), cache=cache)

    service = TranslationService(providers=[primary, secondary])
    assert service.active == "gemini-2.5-flash"

    # Groq est simulé par un appel direct : on vérifie surtout l'ordre et le repli.
    called: list[str] = []
    monkeypatch.setattr(
        secondary,
        "_call",
        lambda prompt: called.append("groq") or json.dumps({"0": "analyste de données"}),
    )
    result = service.translate(["Data analyst"])
    assert result == {"Data analyst": "analyste de données"}
    assert called == ["groq"]


def test_service_without_any_provider_keeps_sources(tmp_path: Path) -> None:
    service = TranslationService(providers=[GeminiTranslator(TranslationSettings(api_key=""))])
    assert not service.enabled
    assert service.active is None
    assert service.translate_safe(["Data analyst"]) == {"Data analyst": "Data analyst"}
