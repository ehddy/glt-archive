from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.models import Novel, Quote, QuoteScrap, Source, User
from app.schemas.schemas import NovelOut, PaginatedQuotesOut, UserPublicOut
from app.services.quote_serializer import serialize_quotes

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/{user_id}", response_model=UserPublicOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/novels", response_model=list[NovelOut])
def get_user_novels(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    direct = db.query(Quote.novel_id).filter(
        Quote.registered_by_id == user_id,
        Quote.novel_id.isnot(None),
    )
    via_source = (
        db.query(Source.novel_id)
        .join(Quote, Quote.id == Source.quote_id)
        .filter(Quote.registered_by_id == user_id, Source.novel_id.isnot(None))
    )
    novel_ids = {row[0] for row in direct} | {row[0] for row in via_source}

    if not novel_ids:
        return []

    return (
        db.query(Novel)
        .options(joinedload(Novel.author))
        .filter(Novel.id.in_(novel_ids))
        .all()
    )


@router.get("/{user_id}/quotes", response_model=PaginatedQuotesOut)
def get_user_quotes(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    total = db.query(Quote).filter(Quote.registered_by_id == user_id).count()
    quotes = (
        db.query(Quote)
        .filter(Quote.registered_by_id == user_id)
        .order_by(Quote.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return PaginatedQuotesOut(
        items=serialize_quotes(db, quotes),
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{user_id}/scraps", response_model=PaginatedQuotesOut)
def get_user_scraps(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    total = db.query(QuoteScrap).filter(QuoteScrap.user_id == user_id).count()
    scraps = (
        db.query(QuoteScrap)
        .filter(QuoteScrap.user_id == user_id)
        .order_by(QuoteScrap.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    quote_ids = [s.quote_id for s in scraps]
    if not quote_ids:
        return PaginatedQuotesOut(items=[], total=total, skip=skip, limit=limit)

    quotes = db.query(Quote).filter(Quote.id.in_(quote_ids)).all()
    quote_map = {q.id: q for q in quotes}
    ordered_quotes = [quote_map[qid] for qid in quote_ids if qid in quote_map]

    return PaginatedQuotesOut(
        items=serialize_quotes(db, ordered_quotes),
        total=total,
        skip=skip,
        limit=limit,
    )
