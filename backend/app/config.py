from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "괴테는 모든 것을 말했다"
    database_url: str = "sqlite:///./quotes.db"

    model_config = {"env_file": ".env", "extra": "ignore"}
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost",
        "http://localhost:80",
    ]


settings = Settings()
