"""Fournisseur Gemini (Google AI Studio) — primaire.

Clé via `OTHELOO_GEMINI_API_KEY`, jamais journalisée : elle voyage dans
l'en-tête `x-goog-api-key` et jamais dans l'URL.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from typing import Any

from orientation.infrastructure.translation.base import (
    USER_AGENT,
    BaseTranslator,
    TranslationSettings,
    TranslationUnavailable,
)

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
# Noms de modèles autorisés : alimente l'URL, donc jamais de contenu libre.
MODEL_PATTERN = re.compile(r"[A-Za-z0-9._-]{1,64}")


class GeminiTranslator(BaseTranslator):
    def _call(self, prompt: str) -> str:
        if not MODEL_PATTERN.fullmatch(self.settings.model):
            raise TranslationUnavailable(f"nom de modèle invalide : {self.settings.model!r}")

        payload = json.dumps(
            {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.0,
                    "responseMimeType": "application/json",
                    "maxOutputTokens": 8192,
                },
            }
        ).encode()
        request = urllib.request.Request(
            ENDPOINT.format(model=self.settings.model),
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.settings.api_key,
                "User-Agent": USER_AGENT,
            },
        )

        last_error: Exception | None = None
        for attempt in range(self.settings.max_retries):
            try:
                # URL constante https + modèle validé : le schéma ne peut pas être détourné.
                with urllib.request.urlopen(request, timeout=self.settings.timeout) as response:  # nosec B310
                    body: dict[str, Any] = json.loads(response.read().decode())
            except urllib.error.HTTPError as error:
                last_error = error
                if error.code in (400, 401, 403, 404):
                    break  # clé, quota ou modèle inconnu : réessayer ne sert à rien
                time.sleep(self.settings.backoff**attempt)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as error:
                last_error = error
                time.sleep(self.settings.backoff**attempt)
            else:
                return self._extract(body)
        raise TranslationUnavailable(str(last_error))

    @staticmethod
    def _extract(body: dict[str, Any]) -> str:
        try:
            parts: list[dict[str, Any]] = body["candidates"][0]["content"]["parts"]
        except (KeyError, IndexError, TypeError) as error:
            raise TranslationUnavailable("réponse Gemini inexploitable") from error
        return "".join(str(part.get("text", "")) for part in parts)


def gemini_settings(api_key: str, **overrides: object) -> TranslationSettings:
    base: dict[str, Any] = {"api_key": api_key}
    base.update(overrides)
    return TranslationSettings(**base)
