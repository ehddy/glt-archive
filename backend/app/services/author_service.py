from sqlalchemy.orm import Session

from app.models.models import Author


def get_or_create_author(db: Session, name: str) -> Author:
    author = db.query(Author).filter(Author.name == name).first()
    if not author:
        author = Author(name=name)
        db.add(author)
        db.flush()
    return author
