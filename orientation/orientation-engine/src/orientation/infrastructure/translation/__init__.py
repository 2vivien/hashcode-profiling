"""Traduction assistée des catalogues externes, avec chaîne de repli."""

from orientation.infrastructure.translation.base import (
    BaseTranslator,
    TranslationCache,
    TranslationSettings,
    TranslationUnavailable,
)
from orientation.infrastructure.translation.gemini import GeminiTranslator
from orientation.infrastructure.translation.groq import GroqTranslator
from orientation.infrastructure.translation.service import TranslationService, build_service

__all__ = [
    "BaseTranslator",
    "GeminiTranslator",
    "GroqTranslator",
    "TranslationCache",
    "TranslationService",
    "TranslationSettings",
    "TranslationUnavailable",
    "build_service",
]
