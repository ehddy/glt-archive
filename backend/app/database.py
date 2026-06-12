from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


def _is_postgres(url: str) -> bool:
    return url.startswith("postgresql") or url.startswith("postgres")


def _engine_kwargs(url: str) -> dict:
    kwargs: dict = {"pool_pre_ping": True}

    if _is_sqlite(url):
        kwargs["connect_args"] = {"check_same_thread": False}
    elif _is_postgres(url):
        connect_args: dict = {}
        if "supabase" in url or "sslmode=" not in url:
            connect_args["sslmode"] = "require"
        kwargs["connect_args"] = connect_args
        if "supabase" in url:
            # Session pooler has a low connection cap; keep the pool small.
            kwargs["pool_size"] = 2
            kwargs["max_overflow"] = 2
            kwargs["pool_timeout"] = 30
        else:
            kwargs["pool_size"] = 5
            kwargs["max_overflow"] = 5

    return kwargs


engine = create_engine(settings.database_url, **_engine_kwargs(settings.database_url))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def database_kind() -> str:
    url = settings.database_url
    if _is_sqlite(url):
        return "sqlite"
    if "supabase" in url:
        return "supabase"
    if _is_postgres(url):
        return "postgresql"
    return "unknown"
