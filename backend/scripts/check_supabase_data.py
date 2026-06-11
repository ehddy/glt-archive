"""Inspect Supabase connection and row counts."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import inspect, text

from app.database import engine, database_kind
from app.config import settings
import re

safe_url = re.sub(r":([^:@/]+)@", ":****@", settings.database_url)
print("DATABASE_URL:", safe_url)
print("kind:", database_kind())
print()

with engine.connect() as conn:
    print("=== connection ===")
    print("database:", conn.execute(text("SELECT current_database()")).scalar())
    print("user:", conn.execute(text("SELECT current_user")).scalar())
    print("schema:", conn.execute(text("SELECT current_schema()")).scalar())
    print()

    tables = inspect(engine).get_table_names(schema="public")
    print("public tables:", tables)
    print()

    print("=== row counts ===")
    for table in ["authors", "novels", "quotes", "quote_versions"]:
        if table in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM public.{table}")).scalar()
            print(f"  {table}: {count}")

    print()
    print("=== authors ===")
    for row in conn.execute(text("SELECT id, name FROM authors ORDER BY id")).fetchall():
        print(f"  {row[0]}: {row[1]}")

    print()
    print("=== novels (first 5) ===")
    for row in conn.execute(
        text("SELECT id, title, author_id FROM novels ORDER BY id LIMIT 5")
    ).fetchall():
        print(f"  {row[0]}: {row[1]} (author {row[2]})")
