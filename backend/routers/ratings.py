from fastapi import APIRouter, Depends
from typing import List

# Servis import'u
from ..services.recommender_service import RecommenderService, get_recommender_service
from ..models.schemas import PredictionRequest, PredictionResponse # Şema dosyalarının var olduğu varsayılır

router = APIRouter(
    prefix="/recommend",
    tags=["Öneri ve Tahmin"]
)

# Pydantic Şemaları (basitleştirilmiş, schemas.py'de tanımlanmalıdır)
# Bu kısmı gerçekte backend/app/models/schemas.py dosyasında tanımlamalısınız.
# Sadece örnek olması için burada tekrar tanımladım.
class PredictionRequest:
    overview: str
    
class PredictionResponse:
    overview: str
    predicted_emotions: List[str]


@router.post("/predict-emotions", response_model=PredictionResponse, summary="Film özetinden duygu etiketlerini tahmin et")
async def predict_movie_emotions(
    request: PredictionRequest,
    recommender_service: RecommenderService = Depends(get_recommender_service)
):
    """
    Kullanıcının sağladığı film özetini alarak, eğitilmiş ML modelleri
    aracılığıyla atanan duygu etiketlerini tahmin eder.
    """
    if not recommender_service.is_ready():
        return {"overview": request.overview, "predicted_emotions": ["HATA: Tahmin servisi yüklenemedi."]}
        
    predicted_labels = recommender_service.predict_emotions(request.overview)
    
    return {
        "overview": request.overview,
        "predicted_emotions": predicted_labels
    }