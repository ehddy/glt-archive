from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.models import Author, Novel, Quote, QuoteVersion
from app.schemas.schemas import QuoteCreate, QuoteUpdate
from app.services.novel_service import import_novel_from_aladin


def _persist_quote(
    db: Session,
    data: QuoteCreate,
    novel_id: int | None,
    author_id: int | None,
) -> Quote:
    quote = Quote(
        text=data.text,
        novel_id=novel_id,
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
    db.commit()
    db.refresh(quote)
    return quote


async def create_quote(db: Session, data: QuoteCreate) -> Quote:
    if data.aladin_item_id:
        novel = await import_novel_from_aladin(db, data.aladin_item_id)
        return _persist_quote(db, data, novel.id, novel.author_id)

    if data.novel_id:
        novel = db.query(Novel).filter(Novel.id == data.novel_id).first()
        if not novel:
            raise ValueError("선택한 작품을 찾을 수 없습니다.")
        return _persist_quote(db, data, novel.id, novel.author_id)

    raise ValueError("연결할 작품을 알라딘 검색으로 선택해 주세요.")


def update_quote(db: Session, quote: Quote, data: QuoteUpdate) -> Quote:
    if data.text is not None:
        quote.text = data.text

    quote.version += 1

    version = QuoteVersion(
        quote_id=quote.id,
        version=quote.version,
        text=quote.text,
    )
    db.add(version)
    db.commit()
    db.refresh(quote)
    return quote


def get_quote(db: Session, quote_id: int) -> Quote | None:
    return (
        db.query(Quote)
        .options(joinedload(Quote.novel).joinedload(Novel.author), joinedload(Quote.author))
        .filter(Quote.id == quote_id)
        .first()
    )


def _quotes_query(db: Session, q: str | None = None, novel_id: int | None = None):
    query = db.query(Quote).options(
        joinedload(Quote.novel).joinedload(Novel.author),
        joinedload(Quote.author),
    )
    if novel_id is not None:
        query = query.filter(Quote.novel_id == novel_id)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        query = (
            query.outerjoin(Novel, Quote.novel_id == Novel.id)
            .outerjoin(Author, Quote.author_id == Author.id)
            .filter(
                or_(
                    Quote.text.ilike(pattern),
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
            query.outerjoin(Novel, Quote.novel_id == Novel.id)
            .outerjoin(Author, Quote.author_id == Author.id)
            .filter(
                or_(
                    Quote.text.ilike(pattern),
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
