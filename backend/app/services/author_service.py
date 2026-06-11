from sqlalchemy.orm import Session

from app.models.models import Author, Novel


def get_or_create_author(db: Session, name: str) -> Author:
    author = db.query(Author).filter(Author.name == name).first()
    if not author:
        author = Author(name=name)
        db.add(author)
        db.flush()
    return author


def get_or_create_novel(db: Session, title: str, author_id: int) -> Novel:
    novel = (
        db.query(Novel)
        .filter(Novel.title == title, Novel.author_id == author_id)
        .first()
    )
    if not novel:
        novel = Novel(title=title, author_id=author_id)
        db.add(novel)
        db.flush()
    return novel
