"""
Film önerileri ile ilgili Pydantic şemaları.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MoodRecommendationResponse(BaseModel):
    """Ruh haline göre film önerisi"""
    
    movie_id: int = Field(..., description="Film ID'si")
    series_title: str = Field(..., description="Film adı")
    genre: str = Field(..., description="Tür")
    imdb_rating: float = Field(..., description="IMDb puanı")
    overview: str = Field(..., description="Film özeti")
    poster_link: Optional[str] = Field(None, description="Poster URL")
    
    class Config:
        from_attributes = True


class PersonalStatsResponse(BaseModel):
    """Kişisel istatistikler"""
    
    watched_count: int = Field(..., description="İzlenen film sayısı")
    liked_count: int = Field(..., description="Beğenilen film sayısı")
    
    class Config:
        from_attributes = True


class RecommendationRequest(BaseModel):
    """Film önerisi isteği"""

    user_id: int = Field(..., description="Kullanıcı ID'si")
    mood: Optional[str] = Field(None, description="Ruh hali")
    genre: Optional[str] = Field(None, description="Film türü")
    limit: int = Field(default=10, ge=1, le=50, description="Kaç film önerilsin")


class RecommendationItem(BaseModel):
    """Önerilen film öğesi"""

    movie_id: int = Field(..., description="Film ID'si")
    series_title: str = Field(..., description="Film adı")
    genre: str = Field(..., description="Film türü")
    imdb_rating: float = Field(..., description="IMDb puanı")
    overview: str = Field(..., description="Film özeti")
    poster_link: Optional[str] = Field(None, description="Poster URL")
    emotion_label: Optional[str] = Field(None, description="İlişkili duygu etiketi")
    
    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Öneriler listesi yanıtı"""

    total: int = Field(..., description="Önerilen film sayısı")
    items: List[RecommendationItem] = Field(..., description="Önerilen filmler")


class PredictEmotionRequest(BaseModel):
    """Duygu tahmini isteği"""

    movie_id: Optional[int] = Field(None, description="Film ID'si")
    overview: Optional[str] = Field(None, description="Film açıklaması")


class PredictEmotionResponse(BaseModel):
    """Duygu tahmini yanıtı"""

    movie_id: Optional[int] = Field(None, description="Film ID'si")
    emotion_label: str = Field(..., description="Tahmin edilen duygu")