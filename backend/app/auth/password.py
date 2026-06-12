import re

import bcrypt

_LETTER_RE = re.compile(r"[A-Za-z]")
_SPECIAL_RE = re.compile(r"[^A-Za-z0-9]")
_BCRYPT_MAX_BYTES = 72


def validate_signup_password(password: str) -> None:
    if len(password) < 8:
        raise ValueError("비밀번호는 8자 이상이어야 해요.")
    if len(password.encode("utf-8")) > _BCRYPT_MAX_BYTES:
        raise ValueError("비밀번호가 너무 길어요.")
    if not _LETTER_RE.search(password):
        raise ValueError("비밀번호에 영문자를 포함해 주세요.")
    if not _SPECIAL_RE.search(password):
        raise ValueError("비밀번호에 특수문자를 포함해 주세요.")


def hash_password(password: str) -> str:
    digest = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return digest.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False
