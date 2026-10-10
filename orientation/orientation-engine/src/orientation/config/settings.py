from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    knowledge_version: str = "v1"
    configuration_version: str = "v1"
    model_version: str = "deterministic-baseline-v1"
    data_service_url: str = ""
    persist: bool = True
    model_config = SettingsConfigDict(env_prefix="OTHELOO_", env_file=".env", extra="ignore")
