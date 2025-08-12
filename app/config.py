from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    openai_api_key: str | None = None
    newsapi_key: str | None = None

    app_name: str = "Company Research Report Generator"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()