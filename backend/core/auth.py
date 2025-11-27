"""
Kimlik doğrulama ve JWT token yönetimi.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config import settings
from backend.db.connection import get_db
from backend.db.models import User
from backend.db.models import RevokedToken, RefreshToken
from sqlalchemy import select
import uuid


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Use HTTP Bearer so OpenAPI/Swagger shows a simple "Bearer" input where
# users can paste a token directly (no OAuth2 password flow).
oauth2_scheme = HTTPBearer()

# Simple in-memory token blacklist for logout support.
# NOTE: This is volatile (cleared on process restart). For production, use Redis or DB.
def revoke_access_token_db(db: Session, token: str, expires_at: Optional[datetime] = None) -> None:
    """Persist a revoked access token in the DB (so it stays revoked across restarts).

    `expires_at` should be set to the JWT `exp` claim (UTC datetime) so we can
    optionally clean up old rows.
    """
    if expires_at is None:
        # best-effort: try to decode exp from token
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            exp_ts = payload.get("exp")
            if exp_ts:
                expires_at = datetime.utcfromtimestamp(exp_ts)
        except Exception:
            expires_at = None

    # Avoid duplicate entries
    existing = db.query(RevokedToken).filter(RevokedToken.token == token).first()
    if existing:
        return

    rt = RevokedToken(token=token, expires_at=expires_at)
    db.add(rt)
    db.commit()


def is_access_token_revoked_db(db: Session, token: str) -> bool:
    """Check DB for revoked access token."""
    if not token:
        return False
    existing = db.query(RevokedToken).filter(RevokedToken.token == token).first()
    return existing is not None


def create_refresh_token(db: Session, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create and persist a refresh token for a user. Returns the raw token string."""
    token = uuid.uuid4().hex
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    rt = RefreshToken(token=token, user_id=user_id, expires_at=expire)
    db.add(rt)
    db.commit()
    return token


def revoke_all_refresh_tokens_for_user(db: Session, user_id: int) -> None:
    """Mark all refresh tokens for the user as revoked."""
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id, RefreshToken.revoked == 0).update({"revoked": 1})
    db.commit()


def verify_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    """Return the RefreshToken row if valid and not revoked/expired."""
    if not token:
        return None
    rt = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not rt:
        return None
    if rt.revoked:
        return None
    if rt.expires_at and rt.expires_at < datetime.utcnow():
        return None
    return rt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWT access token oluşturur"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token_cred: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """JWT token'dan geçerli kullanıcıyı döner"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulama başarısız",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # extract raw token string from HTTPAuthorizationCredentials
    if not token_cred or not token_cred.credentials:
        raise credentials_exception
    token = token_cred.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Check DB-persisted revoked tokens (logout)
    if is_access_token_revoked_db(db, token):
        raise credentials_exception

    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


