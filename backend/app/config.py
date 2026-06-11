import json
from pathlib import Path

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

_DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    "http://localhost",
    "http://localhost:80",
    "http://127.0.0.1",
    "http://127.0.0.1:80",
]


def _parse_cors_origins(value: str | None) -> list[str]:
    if value is None:
        return list(_DEFAULT_CORS_ORIGINS)
    raw = value.strip()
    if not raw:
        return list(_DEFAULT_CORS_ORIGINS)
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return list(_DEFAULT_CORS_ORIGINS)
        if not isinstance(parsed, list):
            return list(_DEFAULT_CORS_ORIGINS)
        origins = [str(origin).strip() for origin in parsed if str(origin).strip()]
        return origins or list(_DEFAULT_CORS_ORIGINS)
    origins = [part.strip() for part in raw.split(",") if part.strip()]
    return origins or list(_DEFAULT_CORS_ORIGINS)


class Settings(BaseSettings):
    app_name: str = "괴테는 모든 것을 말했다"
    database_url: str = "sqlite:///./quotes.db"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"
    aladin_ttb_key: str = ""
    cors_origins_env: str = Field(default="", validation_alias="CORS_ORIGINS")

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return "sqlite:///./quotes.db"
        url = value.strip().strip('"').strip("'")
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    @field_validator("gemini_api_key", "aladin_ttb_key", mode="before")
    @classmethod
    def normalize_api_key(cls, value: str) -> str:
        if not isinstance(value, str):
            return ""
        return value.strip().strip('"').strip("'")

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        return _parse_cors_origins(self.cors_origins_env)

    model_config = {"env_file": str(_ENV_FILE), "extra": "ignore"}


settings = Settings()
