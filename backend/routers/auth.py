from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.auth import create_access_token, get_current_user, get_password_hash, verify_password
from backend.db.connection import get_db
from backend.db.models import User
from backend.schemas.auth import (
    LoginRequest,
    LoginResponse,
    ProfileResponse,
    RegisterRequest,
    RegisterResponse,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponse)
def register_user(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = (
        db.query(User)
        .filter((User.email == body.email) | (User.username == body.username))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email veya kullanıcı adı zaten kullanılıyor",
        )

    user = User(
        username=body.username,
        email=body.email,
        password_hash=get_password_hash(body.password),
        mood=body.mood,
        preferred_genre=body.preferred_genre,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return RegisterResponse(success=True, user_id=user.user_id)


@router.post("/login", response_model=LoginResponse)
def login_user(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı",
        )

    token = create_access_token({"sub": str(user.user_id)})
    return LoginResponse(success=True, token=token, user_id=user.user_id)


@router.get("/profile", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return ProfileResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        mood=current_user.mood,
        preferred_genre=current_user.preferred_genre,
        created_at=current_user.created_at,
    )


