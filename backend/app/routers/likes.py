from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import LikeActionOut, LikeIdsOut, QuoteOut
from app.services import like_service
from app.services.quote_serializer import serialize_quotes

router = APIRouter(prefix="/api/likes", tags=["likes"])


@router.get("", response_model=list[QuoteOut])
def list_likes(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quotes = like_service.list_liked_quotes(db, user.id)
    return serialize_quotes(db, quotes)


@router.get("/ids", response_model=LikeIdsOut)
def list_like_ids(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return LikeIdsOut(quote_ids=like_service.list_liked_quote_ids(db, user.id))


@router.post("/{quote_id}", response_model=LikeActionOut, status_code=201)
def add_like(
    quote_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        like_service.add_like(db, user, quote_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return LikeActionOut(
        quote_id=quote_id,
        liked=True,
        like_count=like_service.get_like_count(db, quote_id),
    )


@router.delete("/{quote_id}", response_model=LikeActionOut)
def remove_like(
    quote_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not like_service.remove_like(db, user, quote_id):
        raise HTTPException(status_code=404, detail="좋아요한 문장이 없습니다.")
    return LikeActionOut(
        quote_id=quote_id,
        liked=False,
        like_count=like_service.get_like_count(db, quote_id),
    )
