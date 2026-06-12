import time



from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import inspect, text

from sqlalchemy.exc import OperationalError



from app.config import settings

from app.database import Base, SessionLocal, database_kind, engine

from app.routers import ai_search, aladin, authors, auth, chat, likes, novels, quotes

from app.seed.loader import seed_database
from app.services.quote_service import migrate_quote_uniqueness
from app.services.source_service import migrate_sources



app = FastAPI(title=settings.app_name)


def _db_busy_message(exc: Exception) -> str | None:
    message = str(exc).lower()
    if "emaxconnsession" in message or "max clients reached" in message:
        return "데이터베이스 연결이 가득 찼어요. 잠시 후 다시 시도해 주세요."
    if "too many connections" in message:
        return "데이터베이스 연결이 많아요. 잠시 후 다시 시도해 주세요."
    return None


@app.exception_handler(RuntimeError)
def runtime_error_handler(_request, exc):
    from fastapi.responses import JSONResponse

    message = str(exc)
    if "데이터베이스" in message:
        return JSONResponse(status_code=503, content={"detail": message})
    return JSONResponse(status_code=500, content={"detail": message})


@app.exception_handler(OperationalError)
def operational_error_handler(_request, exc):
    from fastapi.responses import JSONResponse

    detail = _db_busy_message(exc) or "데이터베이스에 연결하지 못했어요. 잠시 후 다시 시도해 주세요."
    return JSONResponse(status_code=503, content={"detail": detail})


app.add_middleware(

    CORSMiddleware,

    allow_origins=settings.cors_origins,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)



app.include_router(quotes.router)

app.include_router(auth.router)
app.include_router(likes.router)

app.include_router(novels.router)

app.include_router(authors.router)
app.include_router(chat.router)
app.include_router(ai_search.router)
app.include_router(aladin.router)



LEGACY_COLUMNS = {"chapter", "tags", "created_by", "bio", "description"}





NOVEL_ALADIN_COLUMNS = {
    "aladin_item_id": "INTEGER",
    "isbn": "VARCHAR(20)",
    "isbn13": "VARCHAR(20)",
    "publisher": "VARCHAR(200)",
    "pub_date": "VARCHAR(30)",
    "description": "TEXT",
    "cover_url": "VARCHAR(500)",
    "price_sales": "INTEGER",
    "price_standard": "INTEGER",
    "category_name": "VARCHAR(200)",
    "aladin_link": "VARCHAR(500)",
    "detail_json": "TEXT",
}


def migrate_user_columns() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        return

    existing = {col["name"] for col in inspector.get_columns("users")}
    with engine.begin() as conn:
        if "password_hash" not in existing:
            conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))


def migrate_novel_columns() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("novels"):
        return

    existing = {col["name"] for col in inspector.get_columns("novels")}
    with engine.begin() as conn:
        for column, col_type in NOVEL_ALADIN_COLUMNS.items():
            if column not in existing:
                conn.execute(text(f"ALTER TABLE novels ADD COLUMN {column} {col_type}"))


def needs_schema_reset() -> bool:

    inspector = inspect(engine)

    if not inspector.has_table("quotes"):

        return False

    quote_columns = {col["name"] for col in inspector.get_columns("quotes")}

    return bool(LEGACY_COLUMNS & quote_columns)





def init_db(retries: int = 15, delay: float = 3.0):
    db_label = database_kind()
    print(f"[db] using {db_label}")

    for attempt in range(retries):

        try:

            if needs_schema_reset():

                print("[db] legacy schema detected, recreating tables")

                Base.metadata.drop_all(bind=engine)



            Base.metadata.create_all(bind=engine)
            migrate_novel_columns()
            migrate_user_columns()

            db = SessionLocal()

            try:
                migrate_sources(db)
                migrate_quote_uniqueness(db)
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

    return {
        "status": "ok",
        "app": settings.app_name,
        "database": database_kind(),
        "api_version": 2,
        "features": {
            "home_api": True,
            "aladin_search": True,
            "email_auth": True,
            "quote_likes": True,
        },
    }


