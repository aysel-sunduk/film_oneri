"""
Film önerileri endpoint'leri.
- POST /recommendations — Kullanıcıya kişiselleştirilmiş film önerileri (mood, genre)
- POST /predict-emotion — Film açıklamasından duygu tahmini
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.core.auth import get_current_user
from backend.db.connection import get_db
from backend.db.models import Movie, User
from backend.schemas.recommendation import (
    PredictEmotionRequest,
    PredictEmotionResponse,
    RecommendationItem,
    RecommendationRequest,
    RecommendationResponse,
)
from backend.services.recommendation_service import (
    get_recommendations_for_user,
    predict_emotion_for_movie,
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("", response_model=RecommendationResponse)
def get_recommendations(
    body: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Kullanıcıya kişiselleştirilmiş film önerileri sunar.
    - Ruh haline (mood) göre duygu tabanlı filtreleme
    - Tür (genre) tercihine göre filtreleme
    - İzlenmiş filmleri hariç tutar
    - IMDB puanına göre sıralar
    """
    # Kendi önerilerini alıp alamayacağını kontrol et
    if body.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sadece kendi önerilerinizi görüntüleyebilirsiniz",
        )

    # Rekomendasyonları al
    recs = get_recommendations_for_user(
        db=db,
        user_id=body.user_id,
        mood=body.mood,
        genre=body.genre,
        limit=body.limit,
    )

    return RecommendationResponse(total=len(recs), items=recs)


@router.post("/predict-emotion", response_model=PredictEmotionResponse)
def predict_emotion(
    body: PredictEmotionRequest,
    db: Session = Depends(get_db),
):
    """
    Film açıklamasından (overview) duygu tahmini yapar.
    
    İki yol kullanılabilir:
    1. movie_id gönderirsen: veritabanından emotion etiketi getirir
    2. overview gönderirsen: ML modeliyle tahminde bulunur
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



