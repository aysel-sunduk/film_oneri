from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class HistoryCreateRequest(BaseModel):
    user_id: int
    movie_id: int
    interaction: str  # viewed, liked, clicked


class MovieInfo(BaseModel):
    """Film bilgileri (history response için)"""
    movie_id: int
    title: str
    overview: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None
    popularity: Optional[float] = None
    genre: Optional[str] = None
    poster_url: Optional[str] = None
    
    class Config:
        orm_mode = True


class HistoryItemResponse(BaseModel):
    """History item ile birlikte film bilgileri"""
    history_id: int
    movie_id: int
    interaction: str  # viewed, liked, clicked
    watch_date: datetime
    movie: MovieInfo  # Film bilgileri

    class Config:
        orm_mode = True


class HistoryListResponse(BaseModel):
    """History listesi response"""
    total: int
    items: List[HistoryItemResponse]


class HistoryByInteractionResponse(BaseModel):
    """Interaction tipine göre filtrelenmiş history"""
    interaction: str
    total: int
    items: List[HistoryItemResponse]


