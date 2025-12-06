from datetime import datetime, date
from typing import List, Optional

from pydantic import BaseModel


class MovieBase(BaseModel):
    # Dataset kolonları (tam eşleşme)
    title: str
    release_date: Optional[str | date] = None   # ← GÜNCELLENDİ
    overview: str
    popularity: Optional[float] = None
    vote_count: Optional[int] = None
    vote_average: Optional[float] = None
    original_language: Optional[str] = 'en'
    genre: Optional[str] = None
    poster_url: Optional[str] = None


class MovieCreate(MovieBase):
    pass


class MovieUpdate(MovieBase):
    pass


class MovieResponse(MovieBase):
    movie_id: int
    created_at: datetime

    class Config:
        orm_mode = True   # ← SQLAlchemy modellerini düzgün parse eder


class MovieListResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[MovieResponse]
