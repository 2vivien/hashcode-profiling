"""Socle commun aux fournisseurs de traduction.

Les fournisseurs (Gemini, Groq) ne diffèrent que par le transport HTTP et le
format de réponse. Tout le reste — réglages, cache, découpage des lots,
validation stricte de la réponse — vit ici, pour qu'un nouveau fournisseur
s'ajoute sans dupliquer la logique qui protège la qualité.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_GROQ_MODEL = "qwen/qwen3.8-27b"
CACHE_PATH = Path("data/runtime/translation-cache.json")

# Les API publiques filtrent parfois le User-Agent par défaut de la stdlib
# (« Python-urllib/3.12 ») et répondent 403 sans le dire clairement : on
# s'identifie donc comme ce que nous sommes.
USER_AGENT = "hashcode-profiling/1.0 (+https://profiler.otheloo.com)"

# Éléments à ne jamais traduire : codes, sigles, diplômes, niveaux CECRL.
PROTECTED_TOKENS = re.compile(
    r"\b(?:ISC[O0]-\d+|ISCO\d+|SOC\s?\d{2}-\d{3}|O\*NET|ESCO|C1|C2|BTS|DUT|Bac\s?\+?\d?|"
    r"CAP|CAPLP|MSP|DCG|DES|Master|Doctorat|Licence|A1|A2|B1|B2)\b"
)

SYSTEM_PROMPT = (
    "Tu es un traducteur technique spécialisé dans les libellés professionnels. "
    "Tu traduis de l'anglais vers le français des termes de métiers, de compétences "
    "et de formation.\n"
    "Règles strictes :\n"
    "1. Utilise la terminologie française en usage (ex. 'skills' → 'compétences', "
    "'abilities' → 'aptitudes', 'tasks' → 'tâches', 'knowledge' → 'savoirs').\n"
    "2. Ne traduis jamais ces éléments, même s'ils apparaissent dans le texte : {protected}.\n"
    "3. Conserve la casse et la ponctuation d'origine quand cela n'est pas une faute.\n"
    "4. Un métier est un nom de métier : pas de trait d'union artificiel, pas d'article "
    "superflu ('Data analyst' → 'analyste de données', pas 'l'analyste de données').\n"
    "5. Une entrée = une clé. N'écris JAMAIS deux traductions dans une même valeur et "
    "n'omets aucune clé.\n"
    '6. Réponds uniquement par un objet JSON : {{"0": "traduction", "1": "traduction"}}.\n'
    "7. Si une chaîne est vide, renvoie une chaîne vide."
)


class TranslationUnavailable(RuntimeError):
    """Le fournisseur n'a pas pu produire une réponse exploitable."""


@dataclass(frozen=True)
class TranslationSettings:
    api_key: str
    model: str = DEFAULT_GEMINI_MODEL
    target_language: str = "fr"
    source_language: str = "en"
    batch_size: int = 20
    timeout: int = 60
    max_retries: int = 3
    backoff: float = 2.0
    cache_path: Path = CACHE_PATH


def cache_key(text: str, model: str, target: str) -> str:
    return hashlib.sha256(f"{model}|{target}|{text}".encode()).hexdigest()


def strip_fence(text: str) -> str:
    """Les LLM aiment entourer le JSON d'un bloc ```json ; on retire l'enrobage."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def build_prompt(texts: list[str], source: str, target: str) -> str:
    numbered = "\n".join(f"{index}: {text}" for index, text in enumerate(texts))
    return f"{SYSTEM_PROMPT.format(protected=PROTECTED_TOKENS.pattern)}\n\nTraduis ces {len(texts)} chaînes de '{source}' vers '{target}' :\n\n{numbered}\n\nReponds par {{\"0\": \"...\", ...}} avec exactement {len(texts)} clés."


def parse_translations(raw: str, texts: list[str]) -> dict[str, str]:
    """Valide la réponse du modèle.

    On refuse une réponse incomplète : mieux vaut basculer sur un autre
    fournisseur que publier un lot à moitié traduit — ou pire, fusionner deux
    traductions dans une même clé.
    """
    try:
        parsed: object = json.loads(strip_fence(raw))
    except json.JSONDecodeError as error:
        raise TranslationUnavailable("réponse JSON illisible") from error
    if not isinstance(parsed, dict):
        raise TranslationUnavailable("réponse JSON inattendue")

    missing = [index for index in range(len(texts)) if str(index) not in parsed]
    if missing:
        raise TranslationUnavailable(f"réponse incomplète : clés manquantes {missing[:5]}")

    result: dict[str, str] = {}
    for index, text in enumerate(texts):
        value = parsed[str(index)]
        if not isinstance(value, str):
            raise TranslationUnavailable(f"valeur non textuelle pour la clé {index}")
        stripped = value.strip()
        result[text] = stripped if stripped else text
    return result


class TranslationCache:
    """Cache disque : un SHA-256 par chaîne traduite, rechargé à chaque exécution."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._entries: dict[str, str] = {}
        if path.is_file():
            try:
                self._entries = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._entries = {}

    def get(self, key: str) -> str | None:
        return self._entries.get(key)

    def put(self, key: str, value: str) -> None:
        self._entries[key] = value
        self.flush()

    def flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._entries, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        tmp.replace(self.path)

    def __len__(self) -> int:
        return len(self._entries)


class BaseTranslator:
    """Logique commune : cache, lots, repli sur le texte source."""

    settings: TranslationSettings
    cache: TranslationCache

    def __init__(self, settings: TranslationSettings, cache: TranslationCache | None = None) -> None:
        self.settings = settings
        self.cache = cache if cache is not None else TranslationCache(settings.cache_path)

    @property
    def enabled(self) -> bool:
        return bool(self.settings.api_key)

    def needs_translation(self, text: str) -> bool:
        cleaned = text.strip()
        if len(cleaned) < 2:
            return False
        return bool(re.search(r"[a-zA-Z]{3,}", cleaned))

    def _call(self, prompt: str) -> str:  # pragma: no cover - implémenté par les fournisseurs
        raise NotImplementedError

    def _translate_batch(self, texts: list[str]) -> dict[str, str]:
        raw = self._call(build_prompt(texts, self.settings.source_language, self.settings.target_language))
        return parse_translations(raw, texts)

    def translate(self, texts: list[str]) -> dict[str, str]:
        """Traduit par lots. Les chaînes en cache ou vides repartent telles quelles."""
        result: dict[str, str] = {text: text for text in texts}
        pending: list[str] = []
        for text in sorted({text for text in texts if self.needs_translation(text)}):
            cached = self.cache.get(cache_key(text, self.settings.model, self.settings.target_language))
            if cached is not None:
                result[text] = cached
            else:
                pending.append(text)

        size = max(1, self.settings.batch_size)
        for start in range(0, len(pending), size):
            for text, value in self._translate_batch(pending[start : start + size]).items():
                result[text] = value
                self.cache.put(cache_key(text, self.settings.model, self.settings.target_language), value)
        return result

    def translate_safe(self, texts: list[str]) -> dict[str, str]:
        """Comme `translate`, mais jamais d'exception : on garde le texte source."""
        unchanged = {text: text for text in texts}
        if not self.enabled or not texts:
            return unchanged
        try:
            return self.translate(texts)
        except TranslationUnavailable:
            return unchanged
