from sqlalchemy.orm import Session

from app.models.models import Quote
from app.schemas.schemas import AuthorOut, NovelOut, QuoteOut, SourceOut
from app.services import like_service
from app.services.source_service import source_to_dict


def _novel_out(quote: Quote) -> NovelOut | None:
    novel = quote.novel
    if not novel and quote.source and quote.source.novel:
        novel = quote.source.novel
    if not novel:
        return None
    return NovelOut.model_validate(novel)


def _source_out(quote: Quote) -> SourceOut | None:
    if quote.source:
        return SourceOut.model_validate(source_to_dict(quote.source))

    novel = quote.novel
    if not novel:
        return None

    return SourceOut(
        id=0,
        title=novel.title,
        source_type="aladin",
        author=AuthorOut.model_validate(novel.author) if novel.author else None,
        cover_url=novel.cover_url,
        novel_id=novel.id,
        aladin_item_id=novel.aladin_item_id,
        created_at=novel.created_at,
    )


def _author_out(quote: Quote) -> AuthorOut | None:
    if quote.source and quote.source.author:
        return AuthorOut.model_validate(quote.source.author)
    if quote.novel and quote.novel.author:
        return AuthorOut.model_validate(quote.novel.author)
    if quote.author:
        return AuthorOut.model_validate(quote.author)
    return None


def serialize_quote(quote: Quote, *, like_count: int = 0) -> QuoteOut:
    return QuoteOut(
        id=quote.id,
        text=quote.text,
        version=quote.version,
        created_at=quote.created_at,
        updated_at=quote.updated_at,
        like_count=like_count,
        novel=_novel_out(quote),
        source=_source_out(quote),
        author=_author_out(quote),
    )


def serialize_quotes(db: Session, quotes: list[Quote]) -> list[QuoteOut]:
    if not quotes:
        return []
    counts = like_service.get_like_counts(db, [quote.id for quote in quotes])
    return [
        serialize_quote(quote, like_count=counts.get(quote.id, 0))
        for quote in quotes
    ]


def serialize_quote_with_db(db: Session, quote: Quote) -> QuoteOut:
    count = like_service.get_like_count(db, quote.id)
    return serialize_quote(quote, like_count=count)
