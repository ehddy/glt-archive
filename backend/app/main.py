import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import authors, novels, quotes
from app.seed.loader import seed_database

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quotes.router)
app.include_router(novels.router)
app.include_router(authors.router)

LEGACY_COLUMNS = {"chapter", "tags", "created_by", "bio", "description"}


def needs_schema_reset() -> bool:
    inspector = inspect(engine)
    if not inspector.has_table("quotes"):
        return False
    quote_columns = {col["name"] for col in inspector.get_columns("quotes")}
    return bool(LEGACY_COLUMNS & quote_columns)


def init_db(retries: int = 10, delay: float = 2.0):
    for attempt in range(retries):
        try:
            if needs_schema_reset():
                print("[db] legacy schema detected, recreating tables")
                Base.metadata.drop_all(bind=engine)

            Base.metadata.create_all(bind=engine)
            db = SessionLocal()
            try:
                seeded = seed_database(db)
                if seeded:
                    print(f"[seed] loaded {seeded} quotes")
            finally:
                db.close()
            return
        except OperationalError:
            if attempt == retries - 1:
                raise
            print(f"[db] waiting for connection ({attempt + 1}/{retries})")
            time.sleep(delay)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}
