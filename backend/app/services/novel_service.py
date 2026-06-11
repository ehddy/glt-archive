from sqlalchemy.orm import Session, joinedload

from app.models.models import Novel, Quote
from app.schemas.schemas import LibraryOut, NovelWithQuotesOut, QuoteOut


def _quote_out(quote: Quote) -> QuoteOut:
    return QuoteOut.model_validate(quote)


def get_library(db: Session) -> LibraryOut:
    novels = (
        db.query(Novel)
        .options(
            joinedload(Novel.author),
            joinedload(Novel.quotes).joinedload(Quote.author),
        )
        .order_by(Novel.title)
        .all()
    )

    books = []
    for novel in novels:
        quotes = sorted(novel.quotes, key=lambda q: q.updated_at, reverse=True)
        books.append(
            NovelWithQuotesOut(
                id=novel.id,
                title=novel.title,
                author=novel.author,
                quote_count=len(quotes),
                quotes=[_quote_out(q) for q in quotes],
            )
        )

    unlinked_rows = (
        db.query(Quote)
        .options(joinedload(Quote.author))
        .filter(Quote.novel_id.is_(None))
        .order_by(Quote.updated_at.desc())
        .all()
    )
    unlinked = [_quote_out(q) for q in unlinked_rows]

    total_quotes = sum(b.quote_count for b in books) + len(unlinked)

    return LibraryOut(
        books=books,
        unlinked=unlinked,
        total_quotes=total_quotes,
        total_books=len(books),
    )
