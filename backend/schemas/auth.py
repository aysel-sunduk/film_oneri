"""
Kimlik doğrulama ile ilgili Pydantic şemaları.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Kullanıcı kayıt isteği"""

    username: str = Field(..., min_length=3, max_length=50, description="Kullanıcı adı")
    email: EmailStr = Field(..., description="E-posta adresi")
    password: str = Field(
        ..., min_length=6, max_length=100, description="Şifre (min 6 karakter)"
    )
    # Sadece username, email ve password gerekli — diğer alanlar istemiyoruz


class RegisterResponse(BaseModel):
    """Kullanıcı kayıt yanıtı"""

    success: bool = Field(..., description="İşlem başarılı mı")
    user_id: int = Field(..., description="Yeni kullanıcı ID'si")


class LoginRequest(BaseModel):
    """Kullanıcı giriş isteği"""

    email: EmailStr = Field(..., description="E-posta adresi")
    password: str = Field(..., description="Şifre")


class LoginResponse(BaseModel):
    """Kullanıcı giriş yanıtı"""

    success: bool = Field(..., description="İşlem başarılı mı")
    token: str = Field(..., description="JWT access token")
    user_id: int = Field(..., description="Kullanıcı ID'si")


class ProfileResponse(BaseModel):
    """Kullanıcı profil yanıtı"""

    user_id: int = Field(..., description="Kullanıcı ID'si")
    username: str = Field(..., description="Kullanıcı adı")
    email: EmailStr = Field(..., description="E-posta adresi")
    mood: Optional[str] = Field(None, description="Ruh hali")
    preferred_genre: Optional[str] = Field(None, description="Tercih edilen tür")
    created_at: datetime = Field(..., description="Hesap oluşturma tarihi")



