from sqlalchemy.orm import Session

from app.cache import read_cache
from app.config import settings
from app.schemas.schemas import HomeOut, LibraryStatsOut
from app.services import like_service, quote_service
from app.services.novel_service import query_featured_books, query_library_stats
from app.services.quote_serializer import serialize_quotes


def _build_home(
    db: Session,
    *,
    featured_limit: int,
    quote_limit: int,
    user_id: int | None = None,
) -> HomeOut:
    stats = query_library_stats(db)
    featured_books = query_featured_books(db, limit=featured_limit)
    recent = quote_service.list_quotes(db, skip=0, limit=quote_limit)
    liked_ids: list[int] = []
    if user_id:
        liked_ids = like_service.list_liked_quote_ids(db, user_id)

    return HomeOut(
        stats=LibraryStatsOut.model_validate(stats),
        featured_books=featured_books,
        recent_quotes=serialize_quotes(db, recent),
        liked_ids=liked_ids,
    )


def get_home(
    db: Session,
    *,
    featured_limit: int = 10,
    quote_limit: int = 12,
    user_id: int | None = None,
) -> HomeOut:
    user_key = str(user_id) if user_id else "anon"
    cache_key = f"home:{featured_limit}:{quote_limit}:{user_key}"
    ttl = float(settings.cache_ttl_seconds)

    def load() -> dict:
        return _build_home(
            db,
            featured_limit=featured_limit,
            quote_limit=quote_limit,
            user_id=user_id,
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
