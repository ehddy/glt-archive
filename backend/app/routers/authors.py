from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Author
from app.schemas.schemas import AuthorCreate, AuthorOut

router = APIRouter(prefix="/api/authors", tags=["authors"])


@router.get("", response_model=list[AuthorOut])
def list_authors(db: Session = Depends(get_db)):
    authors = db.query(Author).order_by(Author.name).all()
    return [AuthorOut.model_validate(a) for a in authors]


@router.post("", response_model=AuthorOut, status_code=201)
def create_author(data: AuthorCreate, db: Session = Depends(get_db)):
    author = Author(name=data.name)
    db.add(author)
    db.commit()
    db.refresh(author)
    return AuthorOut.model_validate(author)
