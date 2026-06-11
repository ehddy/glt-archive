import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent.parent / "quotes.db"
if not db_path.exists():
    print("quotes.db: not found")
    raise SystemExit(0)

conn = sqlite3.connect(db_path)
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("sqlite tables:", tables)
for table in ["authors", "novels", "quotes"]:
    if table in tables:
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {n}")
conn.close()
