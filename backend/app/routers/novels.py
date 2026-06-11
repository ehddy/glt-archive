from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import (
    LibraryOut,
    NovelDetailOut,
    NovelWithQuotesOut,
    PaginatedNovelsOut,
)
from app.services.novel_service import (
    count_novels,
    get_featured_books,
    get_library,
    get_novel,
    list_novels,
    novel_to_detail_out,
)



router = APIRouter(prefix="/api", tags=["library"])





@router.get("/library", response_model=LibraryOut)

def library(db: Session = Depends(get_db)):

    return get_library(db)


@router.get("/library/featured", response_model=list[NovelWithQuotesOut])
def featured_books(
    limit: int = Query(8, ge=1, le=20),
    db: Session = Depends(get_db),
):
    return get_featured_books(db, limit=limit)


@router.get("/novels", response_model=PaginatedNovelsOut)
def novels_list(
    q: str | None = Query(None, min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(24, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = list_novels(db, skip=skip, limit=limit, q=q)
    total = count_novels(db, q=q)
    return PaginatedNovelsOut(items=items, total=total, skip=skip, limit=limit)


@router.get("/novels/{novel_id}", response_model=NovelDetailOut)
def novel_detail(novel_id: int, db: Session = Depends(get_db)):

    """DB에 저장된 작품 정보를 반환합니다 (알라딘 API 호출 없음)."""

    novel = get_novel(db, novel_id)

    if not novel:

        raise HTTPException(status_code=404, detail="작품을 찾을 수 없습니다.")

    return NovelDetailOut.model_validate(novel_to_detail_out(novel))

