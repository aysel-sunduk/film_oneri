"""
AutoGluon tabanlı duygu tahmini ve film önerisi endpoint'leri
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
import logging

from backend.schemas.recommendation import (
    RecommendationRequest,
    PredictEmotionRequest,
    PredictEmotionResponse,
    EmotionProbability,
    MovieEmotionScore,
    RecommendationResponse,
    RecommendationResponseItem
)
from backend.db.connection import get_db
from backend.db.models import Movie, Emotion
from backend.services.recommender_service import get_recommender_service, RecommenderService
from backend.config import settings

router = APIRouter(prefix="/recommendation", tags=["recommendation"])
logger = logging.getLogger(__name__)

@router.post("/predict-emotions", response_model=PredictEmotionResponse)
async def predict_emotions(
    request: PredictEmotionRequest,
    recommender: RecommenderService = Depends(get_recommender_service)
):
    """
    Verilen film özeti için AutoGluon modeli ile duygu tahmini yapar.
    Olasılık yüzdeleri ile birlikte döner.
    """
    if not recommender.is_ready():
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Model servisi hazır değil",
                "detail": "AutoGluon modeli yüklenemedi.",
                "status": "not_ready"
            }
        )
    
    try:
        # Kullanıcı threshold gönderdi mi?
        auto_threshold = request.threshold is None
        custom_threshold = request.threshold
        
        # Tahmin yap (olasılıklarla birlikte)
        predicted_emotions, emotion_probs, used_threshold = recommender.predict_emotions_with_proba(
            request.overview, 
            auto_threshold=auto_threshold,
            custom_threshold=custom_threshold
        )
        
        # Olasılıkları formatla
        emotion_probabilities = []
        probabilities_summary = {}
        
        for emotion, prob in emotion_probs.items():
            probabilities_summary[emotion] = prob
            emotion_probabilities.append(
                EmotionProbability(
                    emotion=emotion,
                    probability=round(prob, 3),
                    percentage=f"{prob*100:.1f}%"
                )
            )
        
        # En yüksek olasılıklı duyguyu bul
        top_emotion = None
        confidence_score = None
        if emotion_probs:
            sorted_probs = sorted(emotion_probs.items(), key=lambda x: x[1], reverse=True)
            top_emotion = sorted_probs[0][0] if sorted_probs[0][1] > 0 else None
            confidence_score = round(sorted_probs[0][1], 3) if sorted_probs[0][1] > 0 else None
        
        # Olasılıkları büyükten küçüğe sırala
        emotion_probabilities.sort(key=lambda x: x.probability, reverse=True)
        
        return PredictEmotionResponse(
            overview=request.overview,
            predicted_emotions=predicted_emotions,
            emotion_probabilities=emotion_probabilities,
            probabilities_summary=probabilities_summary,
            top_emotion=top_emotion,
            threshold=used_threshold,
            confidence_score=confidence_score,
            status="success",
            model_type="autogluon_multi_label"
        )
        
    except Exception as e:
        logger.error(f"Tahmin hatası: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Tahmin sırasında hata oluştu: {str(e)}"
        )

@router.post("/by-emotions", response_model=RecommendationResponse)
async def get_recommendations_by_emotions(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    recommender: RecommenderService = Depends(get_recommender_service)
):
    """
    Seçilen duygulara göre film önerileri getirir.
    Önce veritabanından etiketlenmiş filmleri çeker, yeterli yoksa model ile ek filmler bulur.
    Her film için duygu olasılık skorlarını da döndürür.
    """
    if not recommender.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Öneri servisi hazır değil. Lütfen önce model eğitildiğinden emin olun."
        )
    
    try:
        # ===== 1. VERİTABANINDAN ETİKETLENMİŞ FİLMLERİ ÇEK (HIZLI) =====
        logger.info(f"Seçilen duygular: {request.selected_emotions}")
        
        # Seçilen duygulara sahip filmleri bul
        emotion_filters = [Emotion.emotion_label == emotion 
                          for emotion in request.selected_emotions]
        
        # Tek sorguda filmleri ve emotion'ları al
        query = db.query(Movie, Emotion.emotion_label)\
            .join(Emotion, Movie.movie_id == Emotion.movie_id)\
            .filter(or_(*emotion_filters))\
            .order_by(Movie.movie_id)
        
        results = query.all()
        
        # Sonuçları film ID'lerine göre grupla
        movie_emotions_map = {}
        movies_map = {}
        
        for movie, emotion_label in results:
            movie_id = movie.movie_id
            movies_map[movie_id] = movie
            
            if movie_id not in movie_emotions_map:
                movie_emotions_map[movie_id] = set()
            if emotion_label:
                movie_emotions_map[movie_id].add(emotion_label)
        
        movies_from_db = list(movies_map.values())
        logger.info(f"Veritabanından {len(movies_from_db)} film bulundu.")
        
        # ===== 2. FİLMLERİ SKORLA =====
        scored_movies = []
        for movie in movies_from_db:
            movie_id = movie.movie_id
            movie_emotion_set = movie_emotions_map.get(movie_id, set())
            
            # Jaccard similarity (veritabanı etiketleri ile)
            intersection = len(movie_emotion_set.intersection(set(request.selected_emotions)))
            union = len(movie_emotion_set.union(set(request.selected_emotions)))
            similarity = intersection / union if union > 0 else 0
            
            # Veritabanından geldiği için bonus skor (+0.2)
            similarity = min(1.0, similarity + 0.2)
            
            # Emotion scores formatla (veritabanı etiketleri için 1.0 skor ver)
            emotion_scores = []
            for emotion in movie_emotion_set:
                if emotion in request.selected_emotions:
                    emotion_scores.append(
                        MovieEmotionScore(
                            emotion=emotion,
                            score=1.0,
                            percentage="100%"
                        )
                    )
            
            scored_movies.append({
                "movie": movie,
                "similarity_score": similarity,
                "predicted_emotions": list(movie_emotion_set),
                "emotion_scores": emotion_scores,
                "matched_emotions": list(movie_emotion_set.intersection(set(request.selected_emotions))),
                "source": "database",
                "confidence": 0.9  # Veritabanından geldiği için yüksek güven
            })
        
        # ===== 3. YETERLİ FİLM YOKSA MODEL İLE EK FİLMLER BUL =====
        if len(scored_movies) < request.max_recommendations:
            logger.info(f"Yeterli film yok ({len(scored_movies)}/{request.max_recommendations}). Model ile ek filmler aranıyor...")
            
            # Henüz skorlanmamış filmleri al
            scored_movie_ids = {m["movie"].movie_id for m in scored_movies}
            
            # Overview'u olan filmleri al (zaten skorlanmamış olanlar)
            candidate_movies = db.query(Movie).filter(
                Movie.overview.isnot(None),
                Movie.overview != "",
                Movie.overview != " ",
                ~Movie.movie_id.in_(scored_movie_ids) if scored_movie_ids else True
            ).limit(500).all()
            
            logger.info(f"{len(candidate_movies)} aday film model ile analiz ediliyor...")
            
            # Her aday film için model tahmini yap
            for movie in candidate_movies:
                try:
                    predicted_emotions, emotion_probs, _ = recommender.predict_emotions_with_proba(
                        movie.overview,
                        auto_threshold=False,
                        custom_threshold=request.emotion_threshold
                    )
                    
                    # Jaccard similarity
                    predicted_set = set(predicted_emotions)
                    requested_set = set(request.selected_emotions)
                    
                    if predicted_set and requested_set:
                        intersection = len(predicted_set.intersection(requested_set))
                        union = len(predicted_set.union(requested_set))
                        similarity = intersection / union if union > 0 else 0
                    else:
                        similarity = 0
                    
                    # Eşik değeri üzerindeki filmleri ekle
                    if similarity >= request.min_similarity_threshold:
                        # Eşleşen duyguların olasılıklarını al
                        matched_probs = [emotion_probs.get(e, 0) for e in predicted_emotions 
                                       if e in request.selected_emotions]
                        avg_confidence = sum(matched_probs) / len(matched_probs) if matched_probs else 0
                        
                        # Duygu skorlarını formatla
                        emotion_scores = []
                        for emotion, prob in emotion_probs.items():
                            if emotion in predicted_emotions and prob > 0:
                                emotion_scores.append(
                                    MovieEmotionScore(
                                        emotion=emotion,
                                        score=round(prob, 3),
                                        percentage=f"{prob*100:.1f}%"
                                    )
                                )
                        emotion_scores.sort(key=lambda x: x.score, reverse=True)
                        
                        scored_movies.append({
                            "movie": movie,
                            "similarity_score": similarity,
                            "predicted_emotions": predicted_emotions,
                            "emotion_scores": emotion_scores,
                            "matched_emotions": list(predicted_set.intersection(requested_set)),
                            "source": "model",
                            "confidence": round(avg_confidence, 3),
                            "emotion_probs": emotion_probs
                        })
                        
                        # Yeterli film bulunduysa dur
                        if len(scored_movies) >= request.max_recommendations * 2:
                            break
                    
                except Exception as e:
                    logger.warning(f"Film {movie.movie_id} için tahmin yapılamadı: {str(e)}")
                    continue
        
        # ===== 4. SKORLAMA VE SIRALAMA =====
        # Similarity + confidence + rating kombinasyonu
        for rec in scored_movies:
            movie = rec["movie"]
            base_score = rec["similarity_score"]
            
            # Rating bonusu (vote_average varsa)
            rating_bonus = 0
            if movie.vote_average:
                rating_bonus = (movie.vote_average - 5.0) / 20.0  # 5.0'dan yüksekse bonus (max 0.25)
            
            # Confidence bonusu
            confidence_bonus = rec.get("confidence", 0) * 0.1
            
            # Final skor
            rec["final_score"] = base_score + rating_bonus + confidence_bonus
        
        # Final skora göre sırala
        scored_movies.sort(key=lambda x: x["final_score"], reverse=True)
        
        # ===== 5. YANITI FORMATLA =====
        recommendations = []
        for rec in scored_movies[:request.max_recommendations]:
            movie = rec["movie"]
            
            # Release year'ı release_date'den çıkar
            release_year = None
            if movie.release_date:
                release_year = movie.release_date.year
            
            # Genre'u listeye çevir
            genres_list = []
            if movie.genre:
                genres_list = [g.strip() for g in movie.genre.split(",")]
            
            recommendations.append(
                RecommendationResponseItem(
                    movie_id=movie.movie_id,
                    title=movie.title,
                    overview=movie.overview[:200] + "..." if len(movie.overview) > 200 else movie.overview,
                    similarity_score=round(rec["similarity_score"], 3),
                    predicted_emotions=rec["predicted_emotions"],
                    emotion_scores=rec["emotion_scores"],
                    matched_emotions=rec["matched_emotions"],
                    poster_url=movie.poster_url,
                    release_year=release_year,
                    rating=movie.vote_average,
                    genres=genres_list if genres_list else None,
                    confidence=round(rec.get("confidence", 0), 3)
                )
            )
        
        logger.info(f"Toplam {len(recommendations)} öneri döndürülüyor.")
        
        return RecommendationResponse(
            selected_emotions=request.selected_emotions,
            total_recommendations=len(recommendations),
            recommendations=recommendations,
            threshold_used=request.emotion_threshold,
            min_similarity_threshold=request.min_similarity_threshold,
            status="success",
            model_type="autogluon_multi_label"
        )
        
    except Exception as e:
        logger.error(f"Öneri sırasında hata oluştu: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Öneri sırasında hata oluştu: {str(e)}"
        )

@router.get("/health")
async def model_health(
    recommender: RecommenderService = Depends(get_recommender_service)
):
    """
    Model servisinin sağlık durumunu kontrol eder.
    """
    return {
        "status": "ready" if recommender.is_ready() else "not_ready",
        "model_type": "autogluon_multi_label",
        "loaded_models": len(recommender.predictors) if hasattr(recommender, 'predictors') else 0,
        "target_labels": list(recommender.target_labels) if hasattr(recommender, 'target_labels') else [],
        "service_available": True
    }

@router.get("/emotion-categories")
async def get_emotion_categories():
    """
    Desteklenen duygu kategorilerini listeler.
    """
    return {
        "emotion_categories": settings.EMOTION_CATEGORIES,
        "total_categories": len(settings.EMOTION_CATEGORIES)
    }

@router.get("/emotions/from-database")
async def get_emotions_from_database(
    db: Session = Depends(get_db),
    include_counts: bool = Query(default=True, description="Her duygunun kaç filmde olduğunu göster")
):
    """
    Veritabanındaki gerçek duygu etiketlerini ve sayılarını döndürür.
    Frontend'de duygu seçimi için kullanılır.
    """
    try:
        # ===== TEK SORGU İLE TÜM DUYGULAR VE SAYILARINI AL =====
        if include_counts:
            # TEK SORGU: GROUP BY ile tüm duygu sayılarını al
            emotion_counts_result = db.query(
                Emotion.emotion_label,
                func.count(Emotion.emotion_id).label('count')
            ).filter(
                Emotion.emotion_label.isnot(None)
            ).group_by(
                Emotion.emotion_label
            ).all()
            
            # Sonuçları işle
            unique_emotions = []
            emotion_counts = {}
            
            for emotion_label, count in emotion_counts_result:
                if emotion_label:
                    unique_emotions.append(emotion_label)
                    emotion_counts[emotion_label] = count
            
            result = {
                "emotions": unique_emotions,
                "total_unique_emotions": len(unique_emotions),
                "emotion_counts": emotion_counts,
                "total_emotion_records": sum(emotion_counts.values()) if emotion_counts else 0,
                "status": "success"
            }
        else:
            # Sadece unique duygular
            emotion_labels = db.query(Emotion.emotion_label).distinct().all()
            unique_emotions = [e[0] for e in emotion_labels if e[0] is not None]
            
            result = {
                "emotions": unique_emotions,
                "total_unique_emotions": len(unique_emotions),
                "status": "success"
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Duygu listesi hatası: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Duygu listesi alınamadı: {str(e)}"
        )

@router.get("/emotion-distribution")
async def get_emotion_distribution(
    db: Session = Depends(get_db),
    recommender: RecommenderService = Depends(get_recommender_service),
    limit: int = Query(default=100, description="Analiz edilecek maksimum film sayısı")
):
    """
    Veritabanındaki filmlerin duygu dağılımını analiz eder.
    """
    if not recommender.is_ready():
        raise HTTPException(status_code=503, detail="Model hazır değil")
    
    try:
        # Overview'u olan filmleri al
        movies = db.query(Movie).filter(
            Movie.overview.isnot(None),
            Movie.overview != "",
            Movie.overview != " "
        ).limit(limit).all()
        
        if not movies:
            return {
                "total_movies_analyzed": 0,
                "total_predictions": 0,
                "emotion_counts": {},
                "emotion_percentages": {},
                "most_common_emotion": None,
                "status": "success",
                "message": "Analiz edilecek film bulunamadı"
            }
        
        # Toplu tahmin yapmak için tüm overview'ları topla
        overviews = [movie.overview for movie in movies if movie.overview]
        
        # Toplu tahmin yap (eğer recommender toplu tahmin destekliyorsa)
        try:
            # Önce tek tek deneyelim, toplu tahmin yoksa
            emotion_counts = {emotion: 0 for emotion in settings.EMOTION_CATEGORIES}
            total_predictions = 0
            
            for movie in movies:
                if movie.overview:
                    emotions, _, _ = recommender.predict_emotions_with_proba(movie.overview)
                    for emotion in emotions:
                        if emotion in emotion_counts:
                            emotion_counts[emotion] += 1
                    total_predictions += len(emotions)
        except Exception as model_error:
            # Model toplu tahmin yapamıyorsa, örnekleme yap
            logger.warning(f"Toplu tahmin başarısız, örnekleme yapılıyor: {model_error}")
            
            # Rastgele 20 film seç
            import random
            sample_size = min(20, len(movies))
            sample_movies = random.sample(movies, sample_size)
            
            emotion_counts = {emotion: 0 for emotion in settings.EMOTION_CATEGORIES}
            total_predictions = 0
            
            for movie in sample_movies:
                if movie.overview:
                    emotions, _, _ = recommender.predict_emotions_with_proba(movie.overview)
                    for emotion in emotions:
                        if emotion in emotion_counts:
                            emotion_counts[emotion] += 1
                    total_predictions += len(emotions)
        
        # Yüzdeleri hesapla
        emotion_percentages = {}
        for emotion, count in emotion_counts.items():
            percentage = (count / total_predictions * 100) if total_predictions > 0 else 0
            emotion_percentages[emotion] = round(percentage, 2)
        
        # En yaygın duyguyu bul
        most_common_emotion = None
        if total_predictions > 0 and emotion_counts:
            most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
        
        return {
            "total_movies_analyzed": len(movies),
            "total_predictions": total_predictions,
            "emotion_counts": emotion_counts,
            "emotion_percentages": emotion_percentages,
            "most_common_emotion": most_common_emotion,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Analiz hatası: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analiz sırasında hata oluştu: {str(e)}"
        )