from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import QuoteVersion
from app.schemas.schemas import (
    PaginatedQuotesOut,
    QuoteCreate,
    QuoteOut,
    QuoteSearchResult,
    QuoteUpdate,
    QuoteVersionOut,
)
from app.services import quote_service
from app.services.search import search_quotes

router = APIRouter(prefix="/api/quotes", tags=["quotes"])


@router.get("", response_model=list[QuoteOut])
def list_quotes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    quotes = quote_service.list_quotes(db, skip=skip, limit=limit)
    return [QuoteOut.model_validate(q) for q in quotes]


@router.get("/browse", response_model=PaginatedQuotesOut)
def browse_quotes(
    q: str | None = Query(None, min_length=1),
    novel_id: int | None = Query(None, ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = quote_service.list_quotes(db, skip=skip, limit=limit, q=q, novel_id=novel_id)
    total = quote_service.count_quotes(db, q=q, novel_id=novel_id)
    return PaginatedQuotesOut(
        items=[QuoteOut.model_validate(q) for q in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/search", response_model=list[QuoteSearchResult])
def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return search_quotes(db, q, limit=limit)


@router.get("/{quote_id}", response_model=QuoteOut)
def get_quote(quote_id: int, db: Session = Depends(get_db)):
    quote = quote_service.get_quote(db, quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="구절을 찾을 수 없습니다.")
    return QuoteOut.model_validate(quote)


@router.get("/{quote_id}/versions", response_model=list[QuoteVersionOut])
def get_versions(quote_id: int, db: Session = Depends(get_db)):
    quote = quote_service.get_quote(db, quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="구절을 찾을 수 없습니다.")
    versions = (
        db.query(QuoteVersion)
        .filter(QuoteVersion.quote_id == quote_id)
        .order_by(QuoteVersion.version.desc())
        .all()
    )
    return [QuoteVersionOut.model_validate(v) for v in versions]


@router.post("", response_model=QuoteOut, status_code=201)
async def create_quote(data: QuoteCreate, db: Session = Depends(get_db)):
    if not data.novel_id and not data.aladin_item_id:
        raise HTTPException(
            status_code=400,
            detail="작품은 알라딘 검색으로 선택해야 합니다. 작가·작품명을 직접 입력할 수 없습니다.",
        )
    try:
        quote = await quote_service.create_quote(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return QuoteOut.model_validate(quote_service.get_quote(db, quote.id))


@router.patch("/{quote_id}", response_model=QuoteOut)
def update_quote(
    quote_id: int, data: QuoteUpdate, db: Session = Depends(get_db)
):
    quote = quote_service.get_quote(db, quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="구절을 찾을 수 없습니다.")
    updated = quote_service.update_quote(db, quote, data)
    return QuoteOut.model_validate(quote_service.get_quote(db, updated.id))
