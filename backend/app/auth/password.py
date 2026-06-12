import re

from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
_LETTER_RE = re.compile(r"[A-Za-z]")
_SPECIAL_RE = re.compile(r"[^A-Za-z0-9]")


def validate_signup_password(password: str) -> None:
    if len(password) < 8:
        raise ValueError("비밀번호는 8자 이상이어야 해요.")
    if not _LETTER_RE.search(password):
        raise ValueError("비밀번호에 영문자를 포함해 주세요.")
    if not _SPECIAL_RE.search(password):
        raise ValueError("비밀번호에 특수문자를 포함해 주세요.")


def hash_password(password: str) -> str:
    return _pwd.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd.verify(password, password_hash)
