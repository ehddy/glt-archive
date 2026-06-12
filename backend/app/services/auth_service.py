from sqlalchemy.orm import Session

from app.auth.password import hash_password, verify_password
from app.models.models import User

LOCAL_PROVIDER = "local"


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(db: Session, email: str) -> User | None:
    normalized = normalize_email(email)
    return db.query(User).filter(User.email == normalized).first()


def get_user_by_provider(db: Session, provider: str, provider_user_id: str) -> User | None:
    return (
        db.query(User)
        .filter(User.provider == provider, User.provider_user_id == provider_user_id)
        .first()
    )


def register_local_user(
    db: Session,
    *,
    email: str,
    password: str,
    name: str | None = None,
) -> User:
    normalized = normalize_email(email)
    if get_user_by_email(db, normalized):
        raise ValueError("이미 가입된 이메일이에요.")

    display_name = (name or "").strip() or normalized.split("@")[0]
    user = User(
        provider=LOCAL_PROVIDER,
        provider_user_id=normalized,
        email=normalized,
        password_hash=hash_password(password),
        name=display_name[:100],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_local_user(db: Session, *, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def upsert_oauth_user(
    db: Session,
    *,
    provider: str,
    provider_user_id: str,
    email: str | None,
    name: str | None,
    avatar_url: str | None,
) -> User:
    """프로덕션 SNS 로그인용 — 추후 사용."""
    user = get_user_by_provider(db, provider, provider_user_id)
    if user:
        changed = False
        if email and user.email != email:
            user.email = email
            changed = True
        if name and user.name != name:
            user.name = name
            changed = True
        if avatar_url and user.avatar_url != avatar_url:
            user.avatar_url = avatar_url
            changed = True
        if changed:
            db.commit()
            db.refresh(user)
        return user

    user = User(
        provider=provider,
        provider_user_id=provider_user_id,
        email=email,
        name=name,
        avatar_url=avatar_url,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
