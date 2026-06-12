from sqlalchemy import inspect, text
from sqlalchemy.orm import Session, joinedload

from app.database import engine
from app.models.models import Author, Novel, Quote, Source
from app.services.author_service import get_or_create_author


def source_to_dict(source: Source) -> dict:
    novel = source.novel
    return {
        "id": source.id,
        "title": source.title,
        "source_type": source.source_type,
        "author": source.author,
        "cover_url": novel.cover_url if novel else None,
        "novel_id": novel.id if novel else None,
        "aladin_item_id": novel.aladin_item_id if novel else None,
        "created_at": source.created_at,
    }


def get_or_create_from_novel(db: Session, novel: Novel) -> Source:
    existing = db.query(Source).filter(Source.novel_id == novel.id).first()
    if existing:
        return existing

    source = Source(
        title=novel.title,
        author_id=novel.author_id,
        source_type="aladin",
        novel_id=novel.id,
    )
    db.add(source)
    db.flush()
    return source


def get_or_create_custom_source(
    db: Session,
    title: str,
    author_name: str | None = None,
) -> Source:
    title = title.strip()[:200]
    author_id = None
    if author_name and author_name.strip():
        author = get_or_create_author(db, author_name.strip()[:100])
        author_id = author.id

    query = db.query(Source).filter(
        Source.source_type == "custom",
        Source.title == title,
        Source.novel_id.is_(None),
    )
    if author_id is None:
        query = query.filter(Source.author_id.is_(None))
    else:
        query = query.filter(Source.author_id == author_id)

    existing = query.first()
    if existing:
        return existing

    source = Source(
        title=title,
        author_id=author_id,
        source_type="custom",
        novel_id=None,
    )
    db.add(source)
    db.flush()
    return source


def get_source(db: Session, source_id: int) -> Source | None:
    return (
        db.query(Source)
        .options(
            joinedload(Source.author),
            joinedload(Source.novel).joinedload(Novel.author),
        )
        .filter(Source.id == source_id)
        .first()
    )


def migrate_sources(db: Session) -> None:
    inspector = inspect(engine)
    if not inspector.has_table("sources"):
        return

    quote_columns: set[str] = set()
    if inspector.has_table("quotes"):
        quote_columns = {col["name"] for col in inspector.get_columns("quotes")}
        if "source_id" not in quote_columns:
            with engine.begin() as conn:
                conn.execute(
                    text("ALTER TABLE quotes ADD COLUMN source_id INTEGER REFERENCES sources(id)")
                )
            quote_columns.add("source_id")

    if "source_id" in quote_columns:
        has_orphan_quotes = (
            db.query(Quote.id).filter(Quote.source_id.is_(None)).limit(1).first()
            is not None
        )
        missing_novel_source = (
            db.query(Novel.id)
            .outerjoin(Source, Source.novel_id == Novel.id)
            .filter(Source.id.is_(None))
            .limit(1)
            .first()
            is not None
        )
        if not has_orphan_quotes and not missing_novel_source:
            return

    novels = db.query(Novel).all()
    for novel in novels:
        existing = db.query(Source).filter(Source.novel_id == novel.id).first()
        if not existing:
            db.add(
                Source(
                    title=novel.title,
                    author_id=novel.author_id,
                    source_type="aladin",
                    novel_id=novel.id,
                )
            )
    db.commit()

    quotes = (
        db.query(Quote)
        .filter(Quote.novel_id.isnot(None), Quote.source_id.is_(None))
        .all()
    )
    for quote in quotes:
        source = db.query(Source).filter(Source.novel_id == quote.novel_id).first()
        if source:
            quote.source_id = source.id
    db.commit()

    orphan_quotes = db.query(Quote).filter(Quote.source_id.is_(None)).all()
    if orphan_quotes:
        fallback = get_or_create_custom_source(db, "미분류")
        for quote in orphan_quotes:
            quote.source_id = fallback.id
        db.commit()

    if inspector.has_table("quotes"):
        quote_columns = {col["name"] for col in inspector.get_columns("quotes")}
        if "source_id" in quote_columns:
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text("ALTER TABLE quotes ALTER COLUMN source_id SET NOT NULL")
                    )
            except Exception:
                pass
