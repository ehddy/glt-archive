from sqlalchemy.orm import Session


def seed_database(db: Session) -> int:
    """시드 데이터는 scripts/reset_aladin_seed.py 로 등록합니다."""
    return 0
