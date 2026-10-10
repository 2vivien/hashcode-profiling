"""Fournisseur Groq (API compatible OpenAI) — repli.

Pourquoi Groq en second : l'offre gratuite de Gemini est plafonnée en
requêtes/minute, et une ingestion de plusieurs milliers de libellés la
sature. Groq sert de filet quand Gemini refuse l'appel (429, quota, panne).

Clé via `OTHELOO_GROQ_API_KEY`.

Choix de modèle : `openai/gpt-oss-*` est un modèle **à raisonnement** — il
consomme tout son budget de tokens à réfléchir et renvoie `content: ""`
avec `finish_reason: "length"`, ce qui est inexploitable pour de la
traduction en lot. On retient donc `qwen/qwen3.8-27b`, qui renvoie
directement le JSON attendu.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from typing import Any

from orientation.infrastructure.translation.base import (
    DEFAULT_GROQ_MODEL,
    USER_AGENT,
    BaseTranslator,
    TranslationSettings,
    TranslationUnavailable,
)

ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
MODEL_PATTERN = re.compile(r"[A-Za-z0-9._/-]{1,64}")


class GroqTranslator(BaseTranslator):
    def _call(self, prompt: str) -> str:
        if not MODEL_PATTERN.fullmatch(self.settings.model):
            raise TranslationUnavailable(f"nom de modèle invalide : {self.settings.model!r}")

        payload = json.dumps(
            {
                "model": self.settings.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "max_tokens": 4096,
            }
        ).encode()
        request = urllib.request.Request(
            ENDPOINT,
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.api_key}",
                # Obligatoire : Groq rejette le User-Agent Python-urllib par défaut (403).
                "User-Agent": USER_AGENT,
            },
        )

        last_error: Exception | None = None
        for attempt in range(self.settings.max_retries):
            try:
                with urllib.request.urlopen(request, timeout=self.settings.timeout) as response:  # nosec B310
                    body: dict[str, Any] = json.loads(response.read().decode())
            except urllib.error.HTTPError as error:
                last_error = error
                if error.code in (401, 403, 404):
                    break
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
            choice: dict[str, Any] = body["choices"][0]
        except (KeyError, IndexError, TypeError) as error:
            raise TranslationUnavailable("réponse Groq inexploitable") from error
        content = str(choice.get("message", {}).get("content") or "").strip()
        if not content:
            # Typique des modèles à raisonnement : le budget part en « reasoning ».
            raise TranslationUnavailable("réponse Groq vide (modèle à raisonnement ?)")
        return content


def groq_settings(api_key: str, **overrides: object) -> TranslationSettings:
    base: dict[str, Any] = {"api_key": api_key, "model": DEFAULT_GROQ_MODEL}
    base.update(overrides)
    return TranslationSettings(**base)
