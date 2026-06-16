from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import QuoteOut, ScrapActionOut, ScrapIdsOut
from app.services import scrap_service
from app.services.quote_serializer import serialize_quotes

router = APIRouter(prefix="/api/scraps", tags=["scraps"])


@router.get("", response_model=list[QuoteOut])
def list_scraps(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    quotes = scrap_service.list_scrapped_quotes(db, user.id)
    return serialize_quotes(db, quotes)


@router.get("/ids", response_model=ScrapIdsOut)
def list_scrap_ids(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ScrapIdsOut(quote_ids=scrap_service.list_scrapped_quote_ids(db, user.id))


@router.post("/{quote_id}", response_model=ScrapActionOut, status_code=201)
def add_scrap(
    quote_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        scrap_service.add_scrap(db, user, quote_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ScrapActionOut(
        quote_id=quote_id,
        scrapped=True,
        scrap_count=scrap_service.get_scrap_count(db, quote_id),
    )


@router.delete("/{quote_id}", response_model=ScrapActionOut)
def remove_scrap(
    quote_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not scrap_service.remove_scrap(db, user, quote_id):
        raise HTTPException(status_code=404, detail="스크랩한 문장이 없습니다.")
    return ScrapActionOut(
        quote_id=quote_id,
        scrapped=False,
        scrap_count=scrap_service.get_scrap_count(db, quote_id),
    )
