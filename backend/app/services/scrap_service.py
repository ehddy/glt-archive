from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.cache import invalidate_read_cache
from app.models.models import Novel, Quote, QuoteScrap, Source, User


def get_scrap_count(db: Session, quote_id: int) -> int:
    return (
        db.query(func.count(QuoteScrap.id))
        .filter(QuoteScrap.quote_id == quote_id)
        .scalar()
        or 0
    )


def get_scrap_counts(db: Session, quote_ids: list[int]) -> dict[int, int]:
    if not quote_ids:
        return {}
    rows = (
        db.query(QuoteScrap.quote_id, func.count(QuoteScrap.id))
        .filter(QuoteScrap.quote_id.in_(quote_ids))
        .group_by(QuoteScrap.quote_id)
        .all()
    )
    counts = {quote_id: 0 for quote_id in quote_ids}
    for quote_id, count in rows:
        counts[quote_id] = int(count)
    return counts


def list_scrapped_quote_ids(db: Session, user_id: int) -> list[int]:
    rows = (
        db.query(QuoteScrap.quote_id)
        .filter(QuoteScrap.user_id == user_id)
        .order_by(QuoteScrap.created_at.desc())
        .all()
    )
    return [row[0] for row in rows]


def list_scrapped_quotes(db: Session, user_id: int) -> list[Quote]:
    rows = (
        db.query(QuoteScrap)
        .filter(QuoteScrap.user_id == user_id)
        .order_by(QuoteScrap.created_at.desc())
        .all()
    )
    if not rows:
        return []

    quote_ids = [row.quote_id for row in rows]
    quotes = (
        db.query(Quote)
        .options(
            joinedload(Quote.source).joinedload(Source.author),
            joinedload(Quote.source).joinedload(Source.novel).joinedload(Novel.author),
            joinedload(Quote.novel).joinedload(Novel.author),
            joinedload(Quote.author),
        )
        .filter(Quote.id.in_(quote_ids))
        .all()
    )
    by_id = {q.id: q for q in quotes}
    return [by_id[qid] for qid in quote_ids if qid in by_id]


def add_scrap(db: Session, user: User, quote_id: int) -> QuoteScrap:
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise ValueError("문장을 찾을 수 없습니다.")

    existing = (
        db.query(QuoteScrap)
        .filter(QuoteScrap.user_id == user.id, QuoteScrap.quote_id == quote_id)
        .first()
    )
    if existing:
        return existing

    scrap = QuoteScrap(user_id=user.id, quote_id=quote_id)
    db.add(scrap)
    db.commit()
    db.refresh(scrap)
    invalidate_read_cache()
    return scrap


def remove_scrap(db: Session, user: User, quote_id: int) -> bool:
    row = (
        db.query(QuoteScrap)
        .filter(QuoteScrap.user_id == user.id, QuoteScrap.quote_id == quote_id)
        .first()
    )
    if not row:
        return False
    db.delete(row)
    db.commit()
    invalidate_read_cache()
    return True
