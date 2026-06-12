from sqlalchemy import func, inspect, or_, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import engine
from app.models.models import Author, Bookmark, Novel, Quote, QuoteVersion, Source
from app.schemas.schemas import QuoteCreate, QuoteUpdate
from app.services.novel_service import import_novel_from_aladin
from app.services.source_service import get_or_create_custom_source, get_or_create_from_novel, get_source
from app.cache import invalidate_read_cache


DUPLICATE_QUOTE_MESSAGE = "이미 등록된 문장입니다."


def _normalize_quote_text(text_value: str) -> str:
    return text_value.strip()


def _find_duplicate_quote(
    db: Session,
    source_id: int,
    text_value: str,
    exclude_quote_id: int | None = None,
) -> Quote | None:
    normalized = _normalize_quote_text(text_value)
    query = db.query(Quote).filter(
        Quote.source_id == source_id,
        Quote.text == normalized,
    )
    if exclude_quote_id is not None:
        query = query.filter(Quote.id != exclude_quote_id)
    return query.first()


def migrate_quote_uniqueness(db: Session) -> None:
    inspector = inspect(engine)
    if not inspector.has_table("quotes"):
        return

    indexes = {idx["name"] for idx in inspector.get_indexes("quotes")}
    if "uq_quote_source_text" in indexes:
        return

    for quote in db.query(Quote).all():
        normalized = _normalize_quote_text(quote.text)
        if quote.text != normalized:
            quote.text = normalized
    db.commit()

    seen: set[tuple[int, str]] = set()
    for quote in db.query(Quote).order_by(Quote.id).all():
        key = (quote.source_id, quote.text)
        if key in seen:
            db.query(Bookmark).filter(Bookmark.quote_id == quote.id).delete(
                synchronize_session=False
            )
            db.query(QuoteVersion).filter(QuoteVersion.quote_id == quote.id).delete(
                synchronize_session=False
            )
            db.delete(quote)
        else:
            seen.add(key)
    db.commit()

    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX uq_quote_source_text "
                    "ON quotes (source_id, text)"
                )
            )
    except Exception:
        try:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE quotes ADD CONSTRAINT uq_quote_source_text "
                        "UNIQUE (source_id, text)"
                    )
                )
        except Exception:
            pass


def _quote_options():
    return (
        joinedload(Quote.source).joinedload(Source.author),
        joinedload(Quote.source).joinedload(Source.novel).joinedload(Novel.author),
        joinedload(Quote.novel).joinedload(Novel.author),
        joinedload(Quote.author),
    )


def _persist_quote(
    db: Session,
    data: QuoteCreate,
    novel_id: int | None,
    source_id: int | None,
    author_id: int | None,
) -> Quote:
    if source_id is None:
        raise ValueError("출처는 필수입니다.")

    normalized_text = _normalize_quote_text(data.text)
    if not normalized_text:
        raise ValueError("문장을 입력해 주세요.")

    if _find_duplicate_quote(db, source_id, normalized_text):
        raise ValueError(DUPLICATE_QUOTE_MESSAGE)

    quote = Quote(
        text=normalized_text,
        novel_id=novel_id,
        source_id=source_id,
        author_id=author_id,
    )
    db.add(quote)
    db.flush()

    version = QuoteVersion(
        quote_id=quote.id,
        version=1,
        text=quote.text,
    )
    db.add(version)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError(DUPLICATE_QUOTE_MESSAGE) from exc
    db.refresh(quote)
    invalidate_read_cache()
    return quote


async def create_quote(db: Session, data: QuoteCreate) -> Quote:
    if data.aladin_item_id:
        novel = await import_novel_from_aladin(db, data.aladin_item_id)
        source = get_or_create_from_novel(db, novel)
        db.commit()
        return _persist_quote(db, data, novel.id, source.id, novel.author_id)

    if data.novel_id:
        novel = db.query(Novel).filter(Novel.id == data.novel_id).first()
        if not novel:
            raise ValueError("선택한 작품을 찾을 수 없습니다.")
        source = get_or_create_from_novel(db, novel)
        db.commit()
        return _persist_quote(db, data, novel.id, source.id, novel.author_id)

    if data.source_id:
        source = get_source(db, data.source_id)
        if not source:
            raise ValueError("선택한 출처를 찾을 수 없습니다.")
        novel_id = source.novel_id
        author_id = source.author_id
        return _persist_quote(db, data, novel_id, source.id, author_id)

    if data.custom_source:
        source = get_or_create_custom_source(
            db,
            data.custom_source.title,
            data.custom_source.author_name,
        )
        db.commit()
        return _persist_quote(db, data, None, source.id, source.author_id)

    raise ValueError("도서를 선택하거나 출처를 직접 입력해 주세요.")


def update_quote(db: Session, quote: Quote, data: QuoteUpdate) -> Quote:
    if data.text is not None:
        normalized_text = _normalize_quote_text(data.text)
        if not normalized_text:
            raise ValueError("문장을 입력해 주세요.")
        if _find_duplicate_quote(
            db,
            quote.source_id,
            normalized_text,
            exclude_quote_id=quote.id,
        ):
            raise ValueError(DUPLICATE_QUOTE_MESSAGE)
        quote.text = normalized_text

    quote.version += 1

    version = QuoteVersion(
        quote_id=quote.id,
        version=quote.version,
        text=quote.text,
    )
    db.add(version)
    db.commit()
    db.refresh(quote)
    invalidate_read_cache()
    return quote


def get_quote(db: Session, quote_id: int) -> Quote | None:
    return (
        db.query(Quote)
        .options(*_quote_options())
        .filter(Quote.id == quote_id)
        .first()
    )


def _quotes_query(db: Session, q: str | None = None, novel_id: int | None = None):
    query = db.query(Quote).options(*_quote_options())
    if novel_id is not None:
        query = query.filter(Quote.novel_id == novel_id)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        query = (
            query.outerjoin(Source, Quote.source_id == Source.id)
            .outerjoin(Novel, Quote.novel_id == Novel.id)
            .outerjoin(Author, Quote.author_id == Author.id)
            .filter(
                or_(
                    Quote.text.ilike(pattern),
                    Source.title.ilike(pattern),
                    Novel.title.ilike(pattern),
                    Author.name.ilike(pattern),
                )
            )
        )
    return query.order_by(Quote.updated_at.desc())


def count_quotes(db: Session, q: str | None = None, novel_id: int | None = None) -> int:
    query = db.query(func.count(Quote.id.distinct()))
    if novel_id is not None:
        query = query.filter(Quote.novel_id == novel_id)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        query = (
            query.outerjoin(Source, Quote.source_id == Source.id)
            .outerjoin(Novel, Quote.novel_id == Novel.id)
            .outerjoin(Author, Quote.author_id == Author.id)
            .filter(
                or_(
                    Quote.text.ilike(pattern),
                    Source.title.ilike(pattern),
                    Novel.title.ilike(pattern),
                    Author.name.ilike(pattern),
                )
            )
        )
    return query.scalar() or 0


def list_quotes(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    q: str | None = None,
    novel_id: int | None = None,
) -> list[Quote]:
    return _quotes_query(db, q=q, novel_id=novel_id).offset(skip).limit(limit).all()
