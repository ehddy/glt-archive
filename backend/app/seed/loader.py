from sqlalchemy.orm import Session

from app.models.models import Quote
from app.schemas.schemas import QuoteCreate
from app.seed.seed_data import SEED_QUOTES
from app.services.quote_service import create_quote


def seed_database(db: Session) -> int:
    existing = db.query(Quote).count()
    if existing > 0:
        return 0

    count = 0
    for item in SEED_QUOTES:
        create_quote(
            db,
            QuoteCreate(
                text=item["text"],
                author_name=item["author"],
                novel_title=item["novel"],
            ),
        )
        count += 1
    return count
