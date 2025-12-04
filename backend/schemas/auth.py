from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    mood: Optional[str] = None
    preferred_genre: Optional[str] = None


class RegisterResponse(BaseModel):
    success: bool
    user_id: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: str
    user_id: int


class ProfileResponse(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    mood: Optional[str] = None
    preferred_genre: Optional[str] = None
    created_at: datetime
