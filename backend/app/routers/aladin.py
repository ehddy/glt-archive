from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.models import Novel
from app.schemas.schemas import AladinBookDetail, AladinBookSearchItem, NovelOut
from app.services.aladin_service import lookup_book, search_books
from app.services.novel_service import import_novel_from_aladin

router = APIRouter(prefix="/api/aladin", tags=["aladin"])


@router.get("/search", response_model=list[AladinBookSearchItem])
async def search(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(10, ge=1, le=30),
):
    results = await search_books(q, max_results=limit)
    return [AladinBookSearchItem.model_validate(item) for item in results]


@router.get("/books/{item_id}", response_model=AladinBookDetail)
async def get_book(item_id: int):
    detail = await lookup_book(item_id)
    return AladinBookDetail.model_validate(detail)


@router.post("/books/{item_id}", response_model=NovelOut, status_code=201)
async def import_book(item_id: int, db: Session = Depends(get_db)):
    novel = await import_novel_from_aladin(db, item_id)
    loaded = (
        db.query(Novel)
        .options(joinedload(Novel.author))
        .filter(Novel.id == novel.id)
        .first()
    )
    if not loaded:
        raise HTTPException(status_code=500, detail="도서 저장에 실패했습니다.")
    return NovelOut.model_validate(loaded)
