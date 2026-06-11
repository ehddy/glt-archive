import re

from sqlalchemy.orm import Session

from app.models.models import Author, Novel, Quote, QuoteVersion
from app.schemas.schemas import QuoteCreate
from app.seed.seed_data import SEED_QUOTES
from app.services.aladin_service import parse_author_name, search_books
from app.services.novel_service import import_novel_from_aladin
from app.services.quote_service import _persist_quote


def _normalize_title(title: str) -> str:
    cleaned = re.sub(r"<br\s*/?>", " ", title, flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    for sep in (" - ", "―", "–", ":"):
        if sep in cleaned:
            cleaned = cleaned.split(sep)[0].strip()
    if "(" in cleaned:
        cleaned = cleaned.split("(")[0].strip()
    return cleaned


def pick_best_aladin_match(
    novel_title: str,
    author_name: str,
    results: list[dict],
) -> dict | None:
    if not results:
        return None

    want_title = _normalize_title(novel_title)
    want_author = author_name.strip()

    def score(item: dict) -> tuple[int, int]:
        title = _normalize_title(item.get("title") or "")
        author = parse_author_name(item.get("author"))
        title_hit = 2 if title == want_title else (1 if want_title in title or title in want_title else 0)
        author_hit = 1 if want_author in author or author in want_author else 0
        return (title_hit, author_hit)

    ranked = sorted(results, key=score, reverse=True)
    best = ranked[0]
    if score(best)[0] == 0:
        return None
    return best


def clear_all_library_data(db: Session) -> None:
    db.query(QuoteVersion).delete()
    db.query(Quote).delete()
    db.query(Novel).delete()
    db.query(Author).delete()
    db.commit()


async def seed_library_from_aladin(db: Session) -> dict:
    """기존 데이터를 삭제하고, 시드 구절·작품을 알라딘 API로 다시 등록합니다."""
    clear_all_library_data(db)

    stats = {
        "novels": 0,
        "quotes": 0,
        "skipped": [],
    }

    for item in SEED_QUOTES:
        novel_title = item["novel"]
        author_name = item["author"]
        text = item["text"]

        results = await search_books(novel_title, max_results=8)
        match = pick_best_aladin_match(novel_title, author_name, results)
        if not match:
            results = await search_books(f"{author_name} {novel_title}", max_results=8)
            match = pick_best_aladin_match(novel_title, author_name, results)
        if not match:
            stats["skipped"].append({"novel": novel_title, "reason": "알라딘에 없음"})
            continue

        novel = await import_novel_from_aladin(db, match["item_id"])
        _persist_quote(
            db,
            QuoteCreate(text=text, novel_id=novel.id, author_id=novel.author_id),
            novel.id,
            novel.author_id,
        )
        stats["novels"] += 1
        stats["quotes"] += 1

    return stats
