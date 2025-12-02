"""
Recommendation için Pydantic şemaları
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any

class PredictEmotionRequest(BaseModel):
    overview: str = Field(..., description="Film özet metni", min_length=10)
    threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Duygu kabul eşiği (0-1 arası). Boş bırakılırsa otomatik belirlenir."
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "overview": "A happy family movie with lots of laughter and fun moments.",
                "threshold": 0.3
            }
        }
    )

class EmotionProbability(BaseModel):
    emotion: str
    probability: float
    percentage: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "emotion": "mutlu",
                "probability": 0.85,
                "percentage": "85%"
            }
        }
    )

class PredictEmotionResponse(BaseModel):
    overview: str
    predicted_emotions: List[str]
    emotion_probabilities: List[EmotionProbability]
    probabilities_summary: Dict[str, float]
    top_emotion: Optional[str] = None
    threshold: float
    confidence_score: Optional[float] = None
    status: str
    model_type: Optional[str] = "autogluon_multi_label"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "overview": "A happy family movie...",
                "predicted_emotions": ["mutlu", "heyecanlı"],
                "emotion_probabilities": [
                    {"emotion": "mutlu", "probability": 0.85, "percentage": "85%"},
                    {"emotion": "heyecanlı", "probability": 0.72, "percentage": "72%"}
                ],
                "probabilities_summary": {"mutlu": 0.85, "heyecanlı": 0.72},
                "top_emotion": "mutlu",
                "threshold": 0.3,
                "confidence_score": 0.78,
                "status": "success",
                "model_type": "autogluon_multi_label"
            }
        }
    )

class RecommendationRequest(BaseModel):
    selected_emotions: List[str] = Field(
        ...,
        description="Öneri için seçilen duygular listesi",
        min_items=1,
        example=["mutlu", "romantik"]
    )
    max_recommendations: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maksimum öneri sayısı"
    )
    min_similarity_threshold: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum benzerlik eşiği"
    )
    emotion_threshold: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Duygu kabul eşiği"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "selected_emotions": ["mutlu", "romantik"],
                "max_recommendations": 10,
                "min_similarity_threshold": 0.3,
                "emotion_threshold": 0.3
            }
        }
    )

class MovieEmotionScore(BaseModel):
    emotion: str
    score: float
    percentage: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "emotion": "mutlu",
                "score": 0.85,
                "percentage": "85%"
            }
        }
    )

class RecommendationResponseItem(BaseModel):
    movie_id: int
    title: str
    overview: str
    similarity_score: float
    predicted_emotions: List[str]
    emotion_scores: List[MovieEmotionScore]
    matched_emotions: List[str]
    poster_url: Optional[str] = None
    release_year: Optional[int] = None
    rating: Optional[float] = None
    genres: Optional[List[str]] = None
    confidence: Optional[float] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "movie_id": 1,
                "title": "The Godfather",
                "overview": "The aging patriarch of an organized crime dynasty...",
                "similarity_score": 0.75,
                "predicted_emotions": ["stresli", "heyecanlı"],
                "emotion_scores": [
                    {"emotion": "stresli", "score": 0.82, "percentage": "82%"},
                    {"emotion": "heyecanlı", "score": 0.65, "percentage": "65%"}
                ],
                "matched_emotions": ["heyecanlı"],
                "poster_url": "http://example.com/poster.jpg",
                "release_year": 1972,
                "rating": 9.2,
                "genres": ["Crime", "Drama"],
                "confidence": 0.73
            }
        }
    )

class RecommendationResponse(BaseModel):
    selected_emotions: List[str]
    total_recommendations: int
    recommendations: List[RecommendationResponseItem]
    threshold_used: float
    min_similarity_threshold: float
    status: str
    model_type: Optional[str] = "autogluon_multi_label"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "selected_emotions": ["mutlu", "romantik"],
                "total_recommendations": 5,
                "recommendations": [],
                "threshold_used": 0.3,
                "min_similarity_threshold": 0.3,
                "status": "success",
                "model_type": "autogluon_multi_label"
            }
        }
    )