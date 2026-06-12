from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.cache import invalidate_read_cache
from app.models.models import Novel, Quote, QuoteLike, Source, User


def get_like_count(db: Session, quote_id: int) -> int:
    return (
        db.query(func.count(QuoteLike.id))
        .filter(QuoteLike.quote_id == quote_id)
        .scalar()
        or 0
    )


def get_like_counts(db: Session, quote_ids: list[int]) -> dict[int, int]:
    if not quote_ids:
        return {}
    rows = (
        db.query(QuoteLike.quote_id, func.count(QuoteLike.id))
        .filter(QuoteLike.quote_id.in_(quote_ids))
        .group_by(QuoteLike.quote_id)
        .all()
    )
    counts = {quote_id: 0 for quote_id in quote_ids}
    for quote_id, count in rows:
        counts[quote_id] = int(count)
    return counts


def list_liked_quote_ids(db: Session, user_id: int) -> list[int]:
    rows = (
        db.query(QuoteLike.quote_id)
        .filter(QuoteLike.user_id == user_id)
        .order_by(QuoteLike.created_at.desc())
        .all()
    )
    return [row[0] for row in rows]


def list_liked_quotes(db: Session, user_id: int) -> list[Quote]:
    rows = (
        db.query(QuoteLike)
        .filter(QuoteLike.user_id == user_id)
        .order_by(QuoteLike.created_at.desc())
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


def add_like(db: Session, user: User, quote_id: int) -> QuoteLike:
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise ValueError("문장을 찾을 수 없습니다.")

    existing = (
        db.query(QuoteLike)
        .filter(QuoteLike.user_id == user.id, QuoteLike.quote_id == quote_id)
        .first()
    )
    if existing:
        return existing

    like = QuoteLike(user_id=user.id, quote_id=quote_id)
    db.add(like)
    db.commit()
    db.refresh(like)
    invalidate_read_cache()
    return like


def remove_like(db: Session, user: User, quote_id: int) -> bool:
    row = (
        db.query(QuoteLike)
        .filter(QuoteLike.user_id == user.id, QuoteLike.quote_id == quote_id)
        .first()
    )
    if not row:
        return False
    db.delete(row)
    db.commit()
    invalidate_read_cache()
    return True
