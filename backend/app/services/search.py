from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.models import Author, Novel, Quote
from app.schemas.schemas import QuoteOut, QuoteSearchResult


def _quote_to_out(quote: Quote) -> QuoteOut:
    return QuoteOut.model_validate(quote)


def search_quotes(db: Session, query: str, limit: int = 20) -> list[QuoteSearchResult]:
    pattern = f"%{query}%"
    quotes = (
        db.query(Quote)
        .outerjoin(Novel, Quote.novel_id == Novel.id)
        .outerjoin(Author, Quote.author_id == Author.id)
        .options(joinedload(Quote.novel).joinedload(Novel.author), joinedload(Quote.author))
        .filter(
            or_(
                Quote.text.ilike(pattern),
                Novel.title.ilike(pattern),
                Author.name.ilike(pattern),
            )
        )
        .order_by(Quote.updated_at.desc())
        .limit(limit)
        .all()
    )
    return [
        QuoteSearchResult(quote=_quote_to_out(q), score=1.0, match_type="text")
        for q in quotes
    ]
