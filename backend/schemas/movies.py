"""
Film ile ilgili Pydantic şemaları.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MovieBase(BaseModel):
    """Film temel bilgileri"""

    series_title: str = Field(..., description="Film adı")
    released_year: Optional[str] = Field(None, description="Yayın yılı")
    genre: Optional[str] = Field(None, description="Tür (virgülle ayrılmış)")
    imdb_rating: Optional[float] = Field(None, ge=0, le=10, description="IMDb puanı")
    meta_score: Optional[int] = Field(None, ge=0, le=100, description="Meta Critic puanı")
    overview: str = Field(..., description="Film özeti")
    director: Optional[str] = Field(None, description="Yönetmen")
    star1: Optional[str] = Field(None, description="1. oyuncu")
    star2: Optional[str] = Field(None, description="2. oyuncu")
    star3: Optional[str] = Field(None, description="3. oyuncu")
    star4: Optional[str] = Field(None, description="4. oyuncu")
    duration: Optional[int] = Field(None, gt=0, description="Süre (dakika)")
    language: Optional[str] = Field(None, description="Dil")
    country: Optional[str] = Field(None, description="Ülke")


class MovieCreate(MovieBase):
    """Yeni film oluşturma"""

    pass


class MovieUpdate(MovieBase):
    """Film güncelleme"""

    pass


class MovieResponse(MovieBase):
    """Film detay yanıtı"""

    movie_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MovieListResponse(BaseModel):
    """Film listesi yanıtı (sayfalandırılmış)"""

    total: int = Field(..., description="Toplam film sayısı")
    page: int = Field(..., ge=1, description="Mevcut sayfa")
    limit: int = Field(..., ge=1, le=100, description="Sayfa başına öğe sayısı")
    items: List[MovieResponse] = Field(..., description="Film listesi")



