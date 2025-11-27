"""
Film öneri endpoint'leri.
- GET /recommendations/mood — Ruh haline göre film önerileri
- GET /recommendations/personal/stats — Kullanıcı istatistikleri
- POST /recommendations — Kişiselleştirilmiş öneriler (mevcut)
- POST /predict-emotion — Duygu tahmini (mevcut)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from backend.core.auth import get_current_user
from backend.db.connection import get_db
from backend.db.models import Movie, User, UserHistory,Emotion
from backend.schemas.recommendation import (
    MoodRecommendationResponse,
    PersonalStatsResponse,
    RecommendationRequest,
    RecommendationResponse,
    PredictEmotionRequest,
    PredictEmotionResponse,
)
from backend.services.recommendation_service import (
    get_recommendations_for_user,
    predict_emotion_for_movie,
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/mood", response_model=List[MoodRecommendationResponse])
def get_mood_recommendations(
    mood: str = Query(..., description="Ruh hali: mutlu, hüzünlü, heyecanlı, rahat, sakin"),
    limit: int = Query(default=10, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ruh haline göre film önerileri
    """
    # Mood'a göre genre mapping
    mood_to_genre = {
        "mutlu": "Comedy,Animation,Musical",
        "hüzünlü": "Drama,Romance", 
        "heyecanlı": "Action,Adventure,Thriller",
        "rahat": "Comedy,Romance,Family",
        "sakin": "Drama,Biography,History"
    }
    
    target_genres = mood_to_genre.get(mood.lower())
    if not target_genres:
        raise HTTPException(400, detail="Geçersiz ruh hali")
    
    # Genre'lere göre filmleri getir (yüksek puanlı)
    movies = db.query(Movie).filter(
        Movie.genre.ilike(f"%{target_genres}%"),
        Movie.imdb_rating >= 7.0
    ).order_by(Movie.imdb_rating.desc()).limit(limit).all()
    
    return movies


@router.get("/personal/stats", response_model=PersonalStatsResponse)
def get_personal_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Kullanıcı istatistiklerini getir
    """
    # İzlenen film sayısı
    watched_count = db.query(UserHistory).filter(
        UserHistory.user_id == current_user.user_id,
        UserHistory.interaction == "watched"
    ).count()
    
    # Beğenilen film sayısı
    liked_count = db.query(UserHistory).filter(
        UserHistory.user_id == current_user.user_id, 
        UserHistory.interaction == "liked"
    ).count()
    
    return PersonalStatsResponse(
        watched_count=watched_count,
        liked_count=liked_count
    )

@router.post("", response_model=RecommendationResponse)
def get_recommendations(
    body: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: user_id={body.user_id}, mood={body.mood}, genre={body.genre}")
    
    # Tüm film sayısını kontrol et
    total_movies = db.query(Movie).count()
    print(f"DEBUG: Toplam film sayısı: {total_movies}")
    
    # Comedy filmleri kontrol et
    comedy_movies = db.query(Movie).filter(Movie.genre.ilike("%comedy%")).count()
    print(f"DEBUG: Comedy film sayısı: {comedy_movies}")
    
    # Emotions tablosunu kontrol et
    emotion_count = db.query(Emotion).count()
    print(f"DEBUG: Emotion kayıt sayısı: {emotion_count}")
    
    # Rekomendasyonları al
    recs = get_recommendations_for_user(
        db=db,
        user_id=body.user_id,
        mood=body.mood,
        genre=body.genre,
        limit=body.limit,
    )
    
    print(f"DEBUG: Bulunan öneriler: {len(recs)}")
    
    return RecommendationResponse(total=len(recs), items=recs)


@router.post("/predict-emotion", response_model=PredictEmotionResponse)
def predict_emotion(
    body: PredictEmotionRequest,
    db: Session = Depends(get_db),
):
    """
    Film açıklamasından (overview) duygu tahmini yapar.
    """
    # Gerekli parametreleri kontrol et
    if body.movie_id is None and not body.overview:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="movie_id veya overview parametresi zorunlu",
        )

    # movie_id geldiyse film var mı kontrolü
    if body.movie_id is not None:
        movie = db.query(Movie).filter(Movie.movie_id == body.movie_id).first()
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Film (ID: {body.movie_id}) bulunamadı",
            )

    # Duygu tahmini yap
    result = predict_emotion_for_movie(
        db=db,
        movie_id=body.movie_id,
        overview=body.overview,
    )

    return PredictEmotionResponse(**result)