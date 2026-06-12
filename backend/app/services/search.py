from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.models import Author, Novel, Quote, Source
from app.schemas.schemas import QuoteSearchResult
from app.services.quote_serializer import serialize_quotes


def search_quotes(db: Session, query: str, limit: int = 20) -> list[QuoteSearchResult]:
    pattern = f"%{query}%"
    quotes = (
        db.query(Quote)
        .outerjoin(Source, Quote.source_id == Source.id)
        .outerjoin(Novel, Quote.novel_id == Novel.id)
        .outerjoin(Author, Quote.author_id == Author.id)
        .options(
            joinedload(Quote.source).joinedload(Source.author),
            joinedload(Quote.source).joinedload(Source.novel).joinedload(Novel.author),
            joinedload(Quote.novel).joinedload(Novel.author),
            joinedload(Quote.author),
        )
        .filter(
            or_(
                Quote.text.ilike(pattern),
                Source.title.ilike(pattern),
                Novel.title.ilike(pattern),
                Author.name.ilike(pattern),
            )
        )
        .order_by(Quote.updated_at.desc())
        .limit(limit)
        .all()
    )
    serialized = serialize_quotes(db, quotes)
    return [
        QuoteSearchResult(quote=quote_out, score=1.0, match_type="text")
        for quote_out in serialized
    ]
