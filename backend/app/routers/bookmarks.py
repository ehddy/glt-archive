from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import BookmarkIdsOut, QuoteOut
from app.services import bookmark_service
from app.services.quote_serializer import serialize_quote
from app.services.quote_service import get_quote

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"])


def _client_id(x_client_id: str | None = Header(default=None, alias="X-Client-Id")) -> str:
    if not x_client_id or len(x_client_id.strip()) < 8:
        raise HTTPException(status_code=400, detail="X-Client-Id 헤더가 필요합니다.")
    return x_client_id.strip()[:64]


@router.get("", response_model=list[QuoteOut])
def list_bookmarks(
    client_id: str = Depends(_client_id),
    db: Session = Depends(get_db),
):
    quotes = bookmark_service.list_bookmarks(db, client_id)
    return [serialize_quote(q) for q in quotes]


@router.get("/ids", response_model=BookmarkIdsOut)
def list_bookmark_ids(
    client_id: str = Depends(_client_id),
    db: Session = Depends(get_db),
):
    return BookmarkIdsOut(
        quote_ids=bookmark_service.list_bookmark_quote_ids(db, client_id)
    )


@router.post("/{quote_id}", response_model=QuoteOut, status_code=201)
def add_bookmark(
    quote_id: int,
    client_id: str = Depends(_client_id),
    db: Session = Depends(get_db),
):
    try:
        bookmark_service.add_bookmark(db, client_id, quote_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    quote = get_quote(db, quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="문장을 찾을 수 없습니다.")
    return serialize_quote(quote)


@router.delete("/{quote_id}", status_code=204)
def remove_bookmark(
    quote_id: int,
    client_id: str = Depends(_client_id),
    db: Session = Depends(get_db),
):
    if not bookmark_service.remove_bookmark(db, client_id, quote_id):
        raise HTTPException(status_code=404, detail="담은 문장이 없습니다.")
