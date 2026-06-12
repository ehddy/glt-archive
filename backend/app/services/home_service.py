from sqlalchemy.orm import Session

from app.cache import read_cache
from app.config import settings
from app.schemas.schemas import HomeOut, LibraryStatsOut
from app.services import bookmark_service, quote_service
from app.services.novel_service import query_featured_books, query_library_stats
from app.services.quote_serializer import serialize_quote


def _build_home(
    db: Session,
    *,
    featured_limit: int,
    quote_limit: int,
    client_id: str | None = None,
) -> HomeOut:
    stats = query_library_stats(db)
    featured_books = query_featured_books(db, limit=featured_limit)
    recent = quote_service.list_quotes(db, skip=0, limit=quote_limit)
    bookmark_ids: list[int] = []
    if client_id:
        bookmark_ids = bookmark_service.list_bookmark_quote_ids(db, client_id)

    return HomeOut(
        stats=LibraryStatsOut.model_validate(stats),
        featured_books=featured_books,
        recent_quotes=[serialize_quote(q) for q in recent],
        bookmark_ids=bookmark_ids,
    )


def get_home(
    db: Session,
    *,
    featured_limit: int = 20,
    quote_limit: int = 12,
    client_id: str | None = None,
) -> HomeOut:
    client_key = client_id or "anon"
    cache_key = f"home:{featured_limit}:{quote_limit}:{client_key}"
    ttl = float(settings.cache_ttl_seconds)

    def load() -> dict:
        return _build_home(
            db,
            featured_limit=featured_limit,
            quote_limit=quote_limit,
            client_id=client_id,
        ).model_dump(mode="json")

    payload = read_cache.get_or_set(
        cache_key,
        load,
        ttl=ttl,
        enabled=settings.cache_enabled,
    )
    if isinstance(payload, HomeOut):
        return payload
    return HomeOut.model_validate(payload)
