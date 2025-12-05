from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class HistoryCreateRequest(BaseModel):
    user_id: int
    movie_id: int
    interaction: str  # viewed, liked, clicked


class MovieInfo(BaseModel):
    """Film bilgileri (history response için)"""
    movie_id: int
    title: str
    overview: Optional[str] = None
    release_date: Optional[date] = None 
    vote_average: Optional[float] = None
    popularity: Optional[float] = None
    genre: Optional[str] = None
    poster_url: Optional[str] = None
    
    # Pydantic v2 için:
    model_config = ConfigDict(from_attributes=True)
    # Pydantic v1 için (eğer v1 kullanıyorsanız):
    # class Config:
    #     orm_mode = True


class HistoryItemResponse(BaseModel):
    """History item ile birlikte film bilgileri"""
    history_id: int
    movie_id: int
    interaction: str  # viewed, liked, clicked
    watch_date: datetime
    movie: MovieInfo  # Film bilgileri

    # Pydantic v2 için:
    model_config = ConfigDict(from_attributes=True)
    # Pydantic v1 için (eğer v1 kullanıyorsanız):
    # class Config:
    #     orm_mode = True


class HistoryListResponse(BaseModel):
    """History listesi response"""
    total: int
    limit: int  # ✅ EKLENDİ
    offset: int  # ✅ EKLENDİ
    items: List[HistoryItemResponse]


class HistoryByInteractionResponse(BaseModel):
    """Interaction tipine göre filtrelenmiş history"""
    interaction: str
    total: int
    limit: int  # ✅ EKLENDİ
    offset: int  # ✅ EKLENDİ
    items: List[HistoryItemResponse]