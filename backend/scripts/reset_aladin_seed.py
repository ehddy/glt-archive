"""기존 DB 데이터를 삭제하고 알라딘 API로 시드 데이터를 다시 등록합니다."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from app.database import SessionLocal, database_kind
from app.seed.aladin_seed import seed_library_from_aladin


async def main() -> None:
    print(f"[reset] database: {database_kind()}")
    db = SessionLocal()
    try:
        stats = await seed_library_from_aladin(db)
        print(f"[reset] novels imported: {stats['novels']}")
        print(f"[reset] quotes created: {stats['quotes']}")
        if stats["skipped"]:
            print("[reset] skipped:")
            for row in stats["skipped"]:
                print(f"  - {row['novel']}: {row['reason']}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
