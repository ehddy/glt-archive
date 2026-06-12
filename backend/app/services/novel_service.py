import json

from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session, joinedload

from app.models.models import Author, Novel, Quote, Source
from app.schemas.schemas import NovelSummaryOut, NovelWithQuotesOut
from app.services.aladin_service import lookup_book, parse_author_name
from app.services.author_service import get_or_create_author
from app.services.quote_serializer import serialize_quote
from app.cache import invalidate_read_cache, read_cache
from app.config import settings


def _quote_out(quote: Quote):
    return serialize_quote(quote)


def query_library_stats(db: Session) -> dict[str, int]:
    row = db.execute(
        text(
            "SELECT "
            "(SELECT COUNT(*) FROM novels), "
            "(SELECT COUNT(*) FROM quotes)"
        )
    ).one()
    return {"total_books": int(row[0] or 0), "total_quotes": int(row[1] or 0)}


def get_library_stats(db: Session) -> dict[str, int]:
    cached = read_cache.get_or_set(
        "stats",
        lambda: query_library_stats(db),
        ttl=float(settings.cache_ttl_seconds),
        enabled=settings.cache_enabled,
    )
    return dict(cached)


def query_featured_books(db: Session, limit: int = 10) -> list[NovelWithQuotesOut]:
    quote_counts = (
        db.query(
            Quote.novel_id,
            func.count(Quote.id).label("quote_count"),
        )
        .filter(Quote.novel_id.isnot(None))
        .group_by(Quote.novel_id)
        .subquery()
    )

    rows = (
        db.query(Novel, quote_counts.c.quote_count)
        .options(joinedload(Novel.author))
        .outerjoin(quote_counts, Novel.id == quote_counts.c.novel_id)
        .order_by(quote_counts.c.quote_count.desc().nullslast(), Novel.title)
        .limit(limit)
        .all()
    )

    return [
        NovelWithQuotesOut(
            id=novel.id,
            title=novel.title,
            author=novel.author,
            quote_count=int(count or 0),
            quotes=[],
            cover_url=novel.cover_url,
            publisher=novel.publisher,
            pub_date=novel.pub_date,
            aladin_item_id=novel.aladin_item_id,
        )
        for novel, count in rows
    ]


def get_featured_books(db: Session, limit: int = 10) -> list[NovelWithQuotesOut]:
    cache_key = f"featured:{limit}"

    def load() -> list[dict]:
        return [
            book.model_dump(mode="json")
            for book in query_featured_books(db, limit=limit)
        ]

    payload = read_cache.get_or_set(
        cache_key,
        load,
        ttl=float(settings.cache_ttl_seconds),
        enabled=settings.cache_enabled,
    )
    return [NovelWithQuotesOut.model_validate(item) for item in payload]


def _novels_browse_query(db: Session, q: str | None = None):
    quote_counts = (
        db.query(
            Quote.novel_id,
            func.count(Quote.id).label("quote_count"),
        )
        .filter(Quote.novel_id.isnot(None))
        .group_by(Quote.novel_id)
        .subquery()
    )
    query = (
        db.query(Novel, quote_counts.c.quote_count)
        .options(joinedload(Novel.author))
        .outerjoin(quote_counts, Novel.id == quote_counts.c.novel_id)
    )
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        query = query.join(Author, isouter=True).filter(
            or_(Novel.title.ilike(pattern), Author.name.ilike(pattern))
        )
    return query


def count_novels(db: Session, q: str | None = None) -> int:
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        return (
            db.query(func.count(Novel.id.distinct()))
            .join(Author, isouter=True)
            .filter(or_(Novel.title.ilike(pattern), Author.name.ilike(pattern)))
            .scalar()
            or 0
        )
    return db.query(func.count(Novel.id)).scalar() or 0


def list_novels(
    db: Session,
    skip: int = 0,
    limit: int = 24,
    q: str | None = None,
) -> list[NovelSummaryOut]:
    rows = (
        _novels_browse_query(db, q=q)
        .order_by(Novel.title)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        NovelSummaryOut(
            id=novel.id,
            title=novel.title,
            author=novel.author,
            quote_count=int(count or 0),
            cover_url=novel.cover_url,
        )
        for novel, count in rows
    ]


def get_novel_by_aladin_id(db: Session, item_id: int) -> Novel | None:
    return db.query(Novel).filter(Novel.aladin_item_id == item_id).first()


def get_novel(db: Session, novel_id: int) -> Novel | None:
    return (
        db.query(Novel)
        .options(
            joinedload(Novel.author),
            joinedload(Novel.quotes).joinedload(Quote.source).joinedload(Source.author),
            joinedload(Novel.quotes).joinedload(Quote.author),
        )
        .filter(Novel.id == novel_id)
        .first()
    )


def _aladin_purchase_link(novel: Novel) -> str | None:
    if novel.aladin_link and novel.aladin_link.strip().startswith("http"):
        return novel.aladin_link.strip()
    if novel.aladin_item_id:
        return f"https://www.aladin.co.kr/shop/wproduct.aspx?ItemId={novel.aladin_item_id}"
    return None


def novel_to_detail_out(novel: Novel) -> dict:
    detail = None
    if novel.detail_json:
        try:
            detail = json.loads(novel.detail_json)
        except json.JSONDecodeError:
            detail = None
    quotes = sorted(novel.quotes or [], key=lambda q: q.updated_at, reverse=True)
    return {
        "id": novel.id,
        "title": novel.title,
        "author_id": novel.author_id,
        "created_at": novel.created_at,
        "author": novel.author,
        "isbn": novel.isbn,
        "isbn13": novel.isbn13,
        "publisher": novel.publisher,
        "pub_date": novel.pub_date,
        "description": novel.description,
        "cover_url": novel.cover_url,
        "price_sales": novel.price_sales,
        "price_standard": novel.price_standard,
        "category_name": novel.category_name,
        "aladin_link": _aladin_purchase_link(novel),
        "aladin_item_id": novel.aladin_item_id,
        "quote_count": len(quotes),
        "quotes": [_quote_out(q) for q in quotes],
        "detail": detail,
    }


def apply_aladin_detail(novel: Novel, detail: dict) -> None:
    novel.title = detail["title"][:200]
    novel.isbn = detail.get("isbn")
    novel.isbn13 = detail.get("isbn13")
    novel.publisher = detail.get("publisher")
    novel.pub_date = detail.get("pub_date")
    novel.description = detail.get("description")
    novel.cover_url = detail.get("cover_url")
    novel.price_sales = detail.get("price_sales")
    novel.price_standard = detail.get("price_standard")
    novel.category_name = detail.get("category_name")
    novel.aladin_link = detail.get("link")
    novel.detail_json = json.dumps(detail.get("detail") or {}, ensure_ascii=False)


async def import_novel_from_aladin(db: Session, item_id: int) -> Novel:
    existing = get_novel_by_aladin_id(db, item_id)
    detail = await lookup_book(item_id)

    author_name = parse_author_name(detail.get("author"))
    author = get_or_create_author(db, author_name)

    if existing:
        existing.author_id = author.id
        apply_aladin_detail(existing, detail)
        db.commit()
        db.refresh(existing)
        invalidate_read_cache()
        return existing

    novel = Novel(
        title=detail["title"][:200],
        author_id=author.id,
        aladin_item_id=item_id,
    )
    apply_aladin_detail(novel, detail)
    db.add(novel)
    db.commit()
    db.refresh(novel)
    invalidate_read_cache()
    return novel
