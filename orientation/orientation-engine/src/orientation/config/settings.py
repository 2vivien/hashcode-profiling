from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    knowledge_version: str = "v1"
    configuration_version: str = "v1"
    model_version: str = "deterministic-baseline-v1"
    data_service_url: str = ""
    persist: bool = True
    # Traduction des catalogues externes (O*NET/ESCO sont en anglais).
    # Les clés ne sont jamais journalisées : elles vivent uniquement dans l'environnement.
    gemini_api_key: str = ""
    groq_api_key: str = ""
    translation_model: str = "gemini-2.5-flash"
    groq_translation_model: str = "qwen/qwen3.8-27b"
    # RAG : embeddings auto (local, gratuit) | hashing | gemini (necessite du quota)
    rag_embedder: str = "auto"
    rag_token_budget: int = 1200
    rag_top_k: int = 8
    translation_target: str = "fr"
    translation_source: str = "en"
    model_config = SettingsConfigDict(env_prefix="OTHELOO_", env_file=".env", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Settings mis en cache : lus une fois par process, pas à chaque requête."""
    return Settings()
