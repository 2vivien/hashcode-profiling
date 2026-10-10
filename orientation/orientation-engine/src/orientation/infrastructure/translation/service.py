"""Chaîne de traduction : un fournisseur primaire, un repli.

Le service essaie Gemini ; si l'appel échoue (quota, 429, réseau, réponse
malformée), il bascule sur Groq. Les deux partagent **le même cache** : une
chaîne déjà payée chez Gemini ne sera jamais re-demandée à Groq, et le SHA-256
du cache porte le nom du modèle qui l'a produite.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from orientation.config.settings import Settings
from orientation.infrastructure.translation.base import (
    CACHE_PATH,
    BaseTranslator,
    TranslationCache,
    TranslationSettings,
    TranslationUnavailable,
)
from orientation.infrastructure.translation.gemini import GeminiTranslator
from orientation.infrastructure.translation.groq import GroqTranslator


@dataclass
class TranslationService:
    providers: list[BaseTranslator] = field(default_factory=list)

    @property
    def enabled(self) -> bool:
        return any(provider.enabled for provider in self.providers)

    @property
    def active(self) -> str | None:
        for provider in self.providers:
            if provider.enabled:
                return provider.settings.model
        return None

    def translate(self, texts: list[str]) -> dict[str, str]:
        """Traduit en descendant la chaîne. Ne lève jamais : garde la source."""
        unchanged = {text: text for text in texts}
        if not texts:
            return unchanged

        live = [provider for provider in self.providers if provider.enabled]
        if not live:
            return unchanged

        # On descend la chaîne ; si tous échouent, la donnée source reste en base.
        for provider in live:
            try:
                return provider.translate(texts)
            except TranslationUnavailable:
                continue
        return unchanged

    def translate_safe(self, texts: list[str]) -> dict[str, str]:
        return self.translate(texts)


def build_service(settings: Settings) -> TranslationService:
    cache = TranslationCache(CACHE_PATH)
    common: dict[str, object] = {
        "target_language": settings.translation_target,
        "source_language": settings.translation_source,
        "cache_path": CACHE_PATH,
    }
    providers: list[BaseTranslator] = []
    if settings.gemini_api_key:
        providers.append(
            GeminiTranslator(
                TranslationSettings(
                    api_key=settings.gemini_api_key,
                    model=settings.translation_model,
                    **{key: value for key, value in common.items()},  # type: ignore[arg-type]
                ),
                cache=cache,
            )
        )
    if settings.groq_api_key:
        providers.append(
            GroqTranslator(
                TranslationSettings(
                    api_key=settings.groq_api_key,
                    model=settings.groq_translation_model,
                    **{key: value for key, value in common.items()},  # type: ignore[arg-type]
                ),
                cache=cache,
            )
        )
    return TranslationService(providers=providers)
