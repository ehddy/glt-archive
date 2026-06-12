from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.jwt import decode_access_token
from app.database import get_db
from app.models.models import User

_bearer = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User | None:
    if not credentials or credentials.scheme.lower() != "bearer":
        return None
    user_id = decode_access_token(credentials.credentials)
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def get_current_user(
    user: User | None = Depends(get_current_user_optional),
) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    return user
