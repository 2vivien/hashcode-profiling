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
    translation_target: str = "fr"
    translation_source: str = "en"
    model_config = SettingsConfigDict(env_prefix="OTHELOO_", env_file=".env", extra="ignore")
