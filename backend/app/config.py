from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    app_name: str = "괴테는 모든 것을 말했다"
    database_url: str = "sqlite:///./quotes.db"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"
    aladin_ttb_key: str = ""

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

    model_config = {"env_file": str(_ENV_FILE), "extra": "ignore"}
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost",
        "http://localhost:80",
    ]


settings = Settings()
