from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import LibraryOut
from app.services.novel_service import get_library

router = APIRouter(prefix="/api", tags=["library"])


@router.get("/library", response_model=LibraryOut)
def library(db: Session = Depends(get_db)):
    return get_library(db)
