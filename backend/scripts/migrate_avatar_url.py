"""One-time migration: widen users.avatar_url from VARCHAR(500) to TEXT."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy import text

from app.database import engine, database_kind

kind = database_kind()
print(f"DB kind: {kind}")

if kind == "sqlite":
    print("SQLite: column type is advisory — no migration needed.")
    sys.exit(0)

with engine.connect() as conn:
    row = conn.execute(text("""
        SELECT data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'avatar_url'
    """)).fetchone()

    if row:
        print(f"Current type: {row[0]}  max_length: {row[1]}")
        if row[0].lower() == "text":
            print("Already TEXT — nothing to do.")
            sys.exit(0)

    print("Running: ALTER TABLE users ALTER COLUMN avatar_url TYPE TEXT ...")
    conn.execute(text("ALTER TABLE users ALTER COLUMN avatar_url TYPE TEXT"))
    conn.commit()
    print("Done.")
