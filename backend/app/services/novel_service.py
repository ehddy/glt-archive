import json

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.models import Author, Novel, Quote
from app.schemas.schemas import LibraryOut, NovelSummaryOut, NovelWithQuotesOut, QuoteOut
from app.services.aladin_service import lookup_book, parse_author_name
from app.services.author_service import get_or_create_author


def _quote_out(quote: Quote) -> QuoteOut:
    return QuoteOut.model_validate(quote)


def get_library(db: Session) -> LibraryOut:
    novels = (
        db.query(Novel)
        .options(
            joinedload(Novel.author),
            joinedload(Novel.quotes).joinedload(Quote.author),
        )
        .order_by(Novel.title)
        .all()
    )

    books = []
    for novel in novels:
        quotes = sorted(novel.quotes, key=lambda q: q.updated_at, reverse=True)
        books.append(
            NovelWithQuotesOut(
                id=novel.id,
                title=novel.title,
                author=novel.author,
                quote_count=len(quotes),
                quotes=[_quote_out(q) for q in quotes],
                cover_url=novel.cover_url,
                publisher=novel.publisher,
                pub_date=novel.pub_date,
                aladin_item_id=novel.aladin_item_id,
            )
        )

    unlinked_rows = (
        db.query(Quote)
        .options(joinedload(Quote.author))
        .filter(Quote.novel_id.is_(None))
        .order_by(Quote.updated_at.desc())
        .all()
    )
    unlinked = [_quote_out(q) for q in unlinked_rows]

    total_quotes = sum(b.quote_count for b in books) + len(unlinked)

    return LibraryOut(
        books=books,
        unlinked=unlinked,
        total_quotes=total_quotes,
        total_books=len(books),
    )


def get_featured_books(db: Session, limit: int = 8) -> list[NovelWithQuotesOut]:
    library = get_library(db)
    ranked = sorted(library.books, key=lambda b: b.quote_count, reverse=True)
    featured = []
    for book in ranked[:limit]:
        featured.append(
            NovelWithQuotesOut(
                id=book.id,
                title=book.title,
                author=book.author,
                quote_count=book.quote_count,
                quotes=[],
                cover_url=book.cover_url,
                publisher=book.publisher,
                pub_date=book.pub_date,
                aladin_item_id=book.aladin_item_id,
            )
        )
    return featured


def _novels_filter_query(db: Session, q: str | None = None):
    query = db.query(Novel).options(
        joinedload(Novel.author),
        joinedload(Novel.quotes),
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
    novels = (
        _novels_filter_query(db, q=q)
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
            quote_count=len(novel.quotes or []),
            cover_url=novel.cover_url,
        )
        for novel in novels
    ]


def get_novel_by_aladin_id(db: Session, item_id: int) -> Novel | None:
    return db.query(Novel).filter(Novel.aladin_item_id == item_id).first()


def get_novel(db: Session, novel_id: int) -> Novel | None:
    return (
        db.query(Novel)
        .options(
            joinedload(Novel.author),
            joinedload(Novel.quotes).joinedload(Quote.author),
        )
        .filter(Novel.id == novel_id)
        .first()
    )


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
        "aladin_link": novel.aladin_link,
        "aladin_item_id": novel.aladin_item_id,
        "quote_count": len(quotes),
        "quotes": [_quote_out(q) for q in quotes],
        "detail": detail,
    }


async def get_novel_detail(db: Session, novel_id: int, refresh: bool = False) -> Novel | None:
    novel = get_novel(db, novel_id)
    if not novel:
        return None
    if refresh and novel.aladin_item_id:
        detail = await lookup_book(novel.aladin_item_id)
        apply_aladin_detail(novel, detail)
        db.commit()
        db.refresh(novel)
    return novel


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
    return novel
