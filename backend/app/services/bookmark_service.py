from sqlalchemy.orm import Session, joinedload

from app.models.models import Bookmark, Novel, Quote


def list_bookmarks(db: Session, client_id: str) -> list[Quote]:
    rows = (
        db.query(Bookmark)
        .filter(Bookmark.client_id == client_id)
        .order_by(Bookmark.created_at.desc())
        .all()
    )
    if not rows:
        return []

    quote_ids = [row.quote_id for row in rows]
    quotes = (
        db.query(Quote)
        .options(joinedload(Quote.novel).joinedload(Novel.author), joinedload(Quote.author))
        .filter(Quote.id.in_(quote_ids))
        .all()
    )
    by_id = {q.id: q for q in quotes}
    return [by_id[qid] for qid in quote_ids if qid in by_id]


def is_bookmarked(db: Session, client_id: str, quote_id: int) -> bool:
    return (
        db.query(Bookmark)
        .filter(Bookmark.client_id == client_id, Bookmark.quote_id == quote_id)
        .first()
        is not None
    )


def add_bookmark(db: Session, client_id: str, quote_id: int) -> Bookmark:
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise ValueError("구절을 찾을 수 없습니다.")

    existing = (
        db.query(Bookmark)
        .filter(Bookmark.client_id == client_id, Bookmark.quote_id == quote_id)
        .first()
    )
    if existing:
        return existing

    bookmark = Bookmark(client_id=client_id, quote_id=quote_id)
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


def remove_bookmark(db: Session, client_id: str, quote_id: int) -> bool:
    row = (
        db.query(Bookmark)
        .filter(Bookmark.client_id == client_id, Bookmark.quote_id == quote_id)
        .first()
    )
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True
