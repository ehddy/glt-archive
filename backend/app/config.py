import json
import os
from pathlib import Path

from pydantic import field_validator
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
]


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
    cors_origins: list[str] = list(_DEFAULT_CORS_ORIGINS)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def merge_cors_origins(cls, value):
        origins: list[str] = []
        if isinstance(value, str):
            raw = value.strip()
            if raw.startswith("["):
                try:
                    origins = json.loads(raw)
                except json.JSONDecodeError:
                    origins = [part.strip() for part in raw.split(",") if part.strip()]
            else:
                origins = [part.strip() for part in raw.split(",") if part.strip()]
        elif isinstance(value, list):
            origins = list(value)

        vercel_url = os.getenv("VERCEL_URL", "").strip()
        if vercel_url:
            origins.append(f"https://{vercel_url}")

        production_url = os.getenv("VERCEL_PROJECT_PRODUCTION_URL", "").strip()
        if production_url:
            origins.append(f"https://{production_url}")

        extra = os.getenv("CORS_ORIGINS", "").strip()
        if extra:
            if extra.startswith("["):
                try:
                    origins.extend(json.loads(extra))
                except json.JSONDecodeError:
                    pass
            else:
                origins.extend(part.strip() for part in extra.split(",") if part.strip())

        # 중복 제거, 순서 유지
        seen: set[str] = set()
        merged: list[str] = []
        for origin in origins:
            if origin and origin not in seen:
                seen.add(origin)
                merged.append(origin)
        return merged or list(_DEFAULT_CORS_ORIGINS)


settings = Settings()
