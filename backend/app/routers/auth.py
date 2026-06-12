from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.auth.jwt import create_access_token
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import AuthTokenOut, LoginRequest, RegisterRequest, UserOut
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _token_response(user: User) -> AuthTokenOut:
    return AuthTokenOut(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
    )


@router.post("/register", response_model=AuthTokenOut, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = auth_service.register_local_user(
            db,
            email=data.email,
            password=data.password,
            name=data.name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _token_response(user)


@router.post("/login", response_model=AuthTokenOut)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate_local_user(
        db,
        email=data.email,
        password=data.password,
    )
    if not user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 맞지 않아요.")
    return _token_response(user)


@router.get("/me", response_model=UserOut)
def auth_me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
