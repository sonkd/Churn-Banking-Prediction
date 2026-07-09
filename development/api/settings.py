"""API configuration, loaded from environment / .env (see development/.env.default).
get_settings() is NOT cached on purpose: request-time endpoints (bucket reads) need to see
env changes within the same process, which is also what makes them straightforward to test
with monkeypatch.setenv(...) per test case."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bucket_uri: str = "./bucket"
    api_url: str = "http://localhost:8000"
    model_dir: str = "./models"


def get_settings() -> Settings:
    return Settings()
