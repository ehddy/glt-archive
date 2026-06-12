from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings

ALGORITHM = "HS256"
OAUTH_STATE_EXPIRE_MINUTES = 10
ACCESS_TOKEN_EXPIRE_DAYS = 30


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_expire_days)
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
    if payload.get("type") != "access":
        return None
    sub = payload.get("sub")
    if not sub:
        return None
    try:
        return int(sub)
    except (TypeError, ValueError):
        return None


def create_oauth_state(provider: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=OAUTH_STATE_EXPIRE_MINUTES)
    payload = {"provider": provider, "exp": expire, "type": "oauth_state"}
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def verify_oauth_state(state: str, provider: str) -> bool:
    try:
        payload = jwt.decode(state, settings.jwt_secret, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return False
    return payload.get("type") == "oauth_state" and payload.get("provider") == provider
