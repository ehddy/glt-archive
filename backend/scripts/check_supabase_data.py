"""Inspect database connection and row counts."""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import inspect, text

from app.database import engine, database_kind
from app.config import settings

safe_url = re.sub(r":([^:@/]+)@", ":****@", settings.database_url)
print("DATABASE_URL:", safe_url)
kind = database_kind()
print("kind:", kind)
print()

is_pg = engine.dialect.name == "postgresql"
schema = "public" if is_pg else None
prefix = "public." if is_pg else ""

with engine.connect() as conn:
    print("=== connection ===")
    if is_pg:
        print("database:", conn.execute(text("SELECT current_database()")).scalar())
        print("user:", conn.execute(text("SELECT current_user")).scalar())
        print("schema:", conn.execute(text("SELECT current_schema()")).scalar())
    else:
        print("file:", engine.url.database)
    print()

    tables = inspect(engine).get_table_names(schema=schema)
    print("tables:", tables)
    print()

    print("=== row counts ===")
    for table in ["authors", "novels", "quotes", "quote_versions"]:
        if table in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {prefix}{table}")).scalar()
            print(f"  {table}: {count}")

    print()
    print("=== authors ===")
    if "authors" in tables:
        for row in conn.execute(text("SELECT id, name FROM authors ORDER BY id")).fetchall():
            print(f"  {row[0]}: {row[1]}")

    print()
    print("=== novels (first 5) ===")
    if "novels" in tables:
        for row in conn.execute(
            text("SELECT id, title, author_id FROM novels ORDER BY id LIMIT 5")
        ).fetchall():
            print(f"  {row[0]}: {row[1]} (author {row[2]})")