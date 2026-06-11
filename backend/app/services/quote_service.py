from sqlalchemy.orm import Session, joinedload

from app.models.models import Author, Novel, Quote, QuoteVersion
from app.schemas.schemas import QuoteCreate, QuoteUpdate


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


def resolve_relations(
    db: Session,
    novel_id: int | None,
    author_id: int | None,
    novel_title: str | None,
    author_name: str | None,
) -> tuple[int | None, int | None]:
    resolved_author_id = author_id
    resolved_novel_id = novel_id

    if author_name and not resolved_author_id:
        author = get_or_create_author(db, author_name)
        resolved_author_id = author.id

    if novel_title and resolved_author_id and not resolved_novel_id:
        novel = get_or_create_novel(db, novel_title, resolved_author_id)
        resolved_novel_id = novel.id

    return resolved_novel_id, resolved_author_id


def create_quote(db: Session, data: QuoteCreate) -> Quote:
    novel_id, author_id = resolve_relations(
        db, data.novel_id, data.author_id, data.novel_title, data.author_name
    )

    quote = Quote(
        text=data.text,
        novel_id=novel_id,
        author_id=author_id,
    )
    db.add(quote)
    db.flush()

    version = QuoteVersion(
        quote_id=quote.id,
        version=1,
        text=quote.text,
    )
    db.add(version)
    db.commit()
    db.refresh(quote)
    return quote


def update_quote(db: Session, quote: Quote, data: QuoteUpdate) -> Quote:
    if data.novel_title or data.author_name:
        novel_id, author_id = resolve_relations(
            db,
            quote.novel_id,
            quote.author_id,
            data.novel_title,
            data.author_name,
        )
        quote.novel_id = novel_id
        quote.author_id = author_id

    if data.text is not None:
        quote.text = data.text

    quote.version += 1

    version = QuoteVersion(
        quote_id=quote.id,
        version=quote.version,
        text=quote.text,
    )
    db.add(version)
    db.commit()
    db.refresh(quote)
    return quote


def get_quote(db: Session, quote_id: int) -> Quote | None:
    return (
        db.query(Quote)
        .options(joinedload(Quote.novel).joinedload(Novel.author), joinedload(Quote.author))
        .filter(Quote.id == quote_id)
        .first()
    )


def list_quotes(db: Session, skip: int = 0, limit: int = 20) -> list[Quote]:
    return (
        db.query(Quote)
        .options(joinedload(Quote.novel).joinedload(Novel.author), joinedload(Quote.author))
        .order_by(Quote.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
