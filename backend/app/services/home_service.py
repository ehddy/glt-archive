from sqlalchemy.orm import Session

from app.schemas.schemas import HomeOut, LibraryStatsOut
from app.services import quote_service
from app.services.novel_service import get_featured_books, get_library_stats
from app.services.quote_serializer import serialize_quote


def get_home(
    db: Session,
    *,
    featured_limit: int = 20,
    quote_limit: int = 12,
) -> HomeOut:
    stats = get_library_stats(db)
    featured_books = get_featured_books(db, limit=featured_limit)
    recent = quote_service.list_quotes(db, skip=0, limit=quote_limit)

    return HomeOut(
        stats=LibraryStatsOut.model_validate(stats),
        featured_books=featured_books,
        recent_quotes=[serialize_quote(q) for q in recent],
    )
