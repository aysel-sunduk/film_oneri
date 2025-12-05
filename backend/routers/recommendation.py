"""
AutoGluon tabanlı duygu tahmini ve film önerisi endpoint'leri
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

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
from backend.db.models import Movie, Emotion, UserHistory
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
    recommender: RecommenderService = Depends(get_recommender_service),
    user_id: Optional[int] = Query(default=None, description="Kullanıcı ID (opsiyonel, geçmişi hariç tutmak için)")
):
    """
    Seçilen duygulara göre film önerileri getirir.
    
    ÇEŞİTLİLİK STRATEJİSİ:
    1. Kullanıcının daha önce izlediği/beğendiği filmleri hariç tutar (user_id varsa)
    2. Her seferinde farklı bir "pencere"den başlar (rastgele rotasyon)
    3. Karma strateji: Popüler + Rastgele + Yeni filmler karışımı
    4. Paralel işleme ile hızlı analiz (9000+ film için optimize)
    """
    if not recommender.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Öneri servisi hazır değil. Lütfen önce model eğitildiğinden emin olun."
        )
    
    try:
        start_time = time.time()
        
        # ===== 1. KULLANICI GEÇMİŞİNİ AL (HARİÇ TUTMAK İÇİN) =====
        excluded_movie_ids = set()
        if user_id:
            # Kullanıcının izlediği/beğendiği filmleri al
            user_history = db.query(UserHistory.movie_id).filter(
                UserHistory.user_id == user_id,
                UserHistory.interaction.in_(["viewed", "liked"])
            ).all()
            excluded_movie_ids = {h[0] for h in user_history}
            logger.info(f"Kullanıcı geçmişi: {len(excluded_movie_ids)} film hariç tutulacak.")
        
        # ===== 2. VERİTABANINDAN ETİKETLENMİŞ FİLMLERİ ÇEK =====
        logger.info(f"Seçilen duygular: {request.selected_emotions}")
        
        emotion_filters = [Emotion.emotion_label == emotion 
                          for emotion in request.selected_emotions]
        
        query = db.query(Movie, Emotion.emotion_label)\
            .join(Emotion, Movie.movie_id == Emotion.movie_id)\
            .filter(or_(*emotion_filters))\
            .order_by(Movie.movie_id)
        
        # Kullanıcı geçmişini hariç tut
        if excluded_movie_ids:
            query = query.filter(~Movie.movie_id.in_(excluded_movie_ids))
        
        results = query.all()
        
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
        logger.info(f"Veritabanından {len(movies_from_db)} film bulundu (kullanıcı geçmişi hariç).")
        
        # Veritabanından gelen filmleri RASTGELE KARIŞTIR (çeşitlilik için)
        random.shuffle(movies_from_db)
        
        # ===== 3. VERİTABANI FİLMLERİNİ SKORLA =====
        scored_movies = []
        for movie in movies_from_db:
            movie_id = movie.movie_id
            movie_emotion_set = movie_emotions_map.get(movie_id, set())
            
            # OLASILIK AĞIRLIKLI SIMILARITY (veritabanı filmleri için)
            intersection = len(movie_emotion_set.intersection(set(request.selected_emotions)))
            union = len(movie_emotion_set.union(set(request.selected_emotions)))
            jaccard_similarity = intersection / union if union > 0 else 0
            
            # Veritabanı filmleri için: Eşleşen duygu sayısı / Seçilen duygu sayısı
            # (Tüm eşleşen duygular %100 güvenilir olduğu için)
            prob_weighted = intersection / len(request.selected_emotions) if request.selected_emotions else 0
            
            # İkisini birleştir (olasılık ağırlıklı daha önemli)
            similarity = (prob_weighted * 0.7) + (jaccard_similarity * 0.3)
            
            # Küçük rastgele faktör (çeşitlilik için, ama çok güçlü değil)
            random_bonus = random.uniform(0.02, 0.08)  # 0.02-0.08 arası (azaltıldı)
            similarity = min(1.0, similarity + random_bonus)
            
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
                "confidence": 0.9
            })
        
        # ===== 4. KARMA STRATEJİ: POPÜLER + RASTGELE + YENİ =====
        scored_movie_ids = {m["movie"].movie_id for m in scored_movies}
        scored_movie_ids.update(excluded_movie_ids)  # Kullanıcı geçmişini de ekle
        
        # SQL parametre limiti sorununu önlemek için: Eğer çok fazla ID varsa, sadece son 1000'ini kullan
        # (Zaten veritabanından gelen filmler zaten skorlandı, sadece yeni filmler için filtreleme yapıyoruz)
        MAX_SQL_PARAMS = 1000  # PostgreSQL için güvenli limit
        excluded_ids_list = list(scored_movie_ids)
        if len(excluded_ids_list) > MAX_SQL_PARAMS:
            # Son 1000 ID'yi kullan (en yeni eklenenler)
            excluded_ids_list = excluded_ids_list[-MAX_SQL_PARAMS:]
            logger.warning(f"Çok fazla hariç tutulacak film var ({len(scored_movie_ids)}). Son {MAX_SQL_PARAMS} tanesi kullanılıyor.")
        
        # Toplam kaç film var?
        base_query = db.query(Movie).filter(
            Movie.overview.isnot(None),
            Movie.overview != "",
            Movie.overview != " "
        )
        if excluded_ids_list:
            base_query = base_query.filter(~Movie.movie_id.in_(excluded_ids_list))
        total_movies_count = base_query.count()
        
        logger.info(f"Toplam {total_movies_count} aday film mevcut (hariç tutulan: {len(scored_movie_ids)}).")
        
        # ===== GENRE FİLTRELEME: Seçilen duygulara göre uygun genre'ları bul =====
        preferred_genres = set()
        for emotion in request.selected_emotions:
            if emotion in settings.EMOTION_GENRE_MAP:
                preferred_genres.update(settings.EMOTION_GENRE_MAP[emotion])
        
        logger.info(f"Seçilen duygular için uygun genre'lar: {preferred_genres}")
        
        # Genre filtreleme helper fonksiyonu
        def add_genre_filter(query):
            """Genre filtreleme ekler (opsiyonel - eğer genre varsa)"""
            if preferred_genres:
                # Genre string'inde bu genre'lardan herhangi biri var mı?
                genre_filters = [Movie.genre.ilike(f"%{genre}%") for genre in preferred_genres]
                return query.filter(or_(*genre_filters))
            return query
        
        # ===== RASTGELE ROTASYON: Her seferinde farklı başlangıç noktası =====
        # Rastgele bir seed oluştur (her istek için farklı)
        random_seed = random.randint(1, 1000000)
        random.seed(random_seed)
        logger.info(f"Rastgele seed: {random_seed}")
        
        # ===== STRATEJİ 1: POPÜLER FİLMLER (%30) - Genre'e uygun + Rastgele karıştırılmış =====
        popular_count = int(request.max_recommendations * 0.3)
        popular_query = db.query(Movie).filter(
            Movie.overview.isnot(None),
            Movie.overview != "",
            Movie.overview != " "
        )
        if excluded_ids_list:
            popular_query = popular_query.filter(~Movie.movie_id.in_(excluded_ids_list))
        
        # Önce genre'e uygun filmleri al (öncelikli)
        popular_with_genre = add_genre_filter(popular_query)
        popular_movies = popular_with_genre.order_by(
            desc(Movie.vote_average),
            desc(Movie.popularity)
        ).limit(popular_count * 5).all()
        
        # Eğer yeterli film yoksa, genre'e uygun olmayanları da ekle
        if len(popular_movies) < popular_count * 3:
            popular_without_genre = popular_query.filter(
                ~or_(*[Movie.genre.ilike(f"%{genre}%") for genre in preferred_genres]) if preferred_genres else True
            ).order_by(
                desc(Movie.vote_average),
                desc(Movie.popularity)
            ).limit((popular_count * 3) - len(popular_movies)).all()
            popular_movies.extend(popular_without_genre)
        
        # Rastgele karıştır
        random.shuffle(popular_movies)
        popular_movies = popular_movies[:popular_count * 3]  # İlk 3 katını al
        
        # ===== STRATEJİ 2: RASTGELE FİLMLER (%50) - Genre'e uygun + Tamamen rastgele =====
        random_count = int(request.max_recommendations * 0.5)
        random_query = db.query(Movie).filter(
            Movie.overview.isnot(None),
            Movie.overview != "",
            Movie.overview != " "
        )
        if excluded_ids_list:
            random_query = random_query.filter(~Movie.movie_id.in_(excluded_ids_list))
        
        # Önce genre'e uygun filmleri al (öncelikli)
        random_with_genre = add_genre_filter(random_query)
        try:
            random_movies = random_with_genre.order_by(func.random()).limit(random_count * 3).all()
        except:
            random_offset = random.randint(0, max(0, total_movies_count - random_count * 3))
            random_movies = random_with_genre.order_by(Movie.movie_id).offset(random_offset).limit(random_count * 3).all()
        
        # Eğer yeterli film yoksa, genre'e uygun olmayanları da ekle
        if len(random_movies) < random_count * 3:
            random_without_genre = random_query.filter(
                ~or_(*[Movie.genre.ilike(f"%{genre}%") for genre in preferred_genres]) if preferred_genres else True
            )
            try:
                additional = random_without_genre.order_by(func.random()).limit((random_count * 3) - len(random_movies)).all()
            except:
                random_offset = random.randint(0, max(0, total_movies_count - random_count * 3))
                additional = random_without_genre.order_by(Movie.movie_id).offset(random_offset).limit((random_count * 3) - len(random_movies)).all()
            random_movies.extend(additional)
        
        # ===== STRATEJİ 3: YENİ FİLMLER (%20) - Genre'e uygun + Rastgele karıştırılmış =====
        new_count = int(request.max_recommendations * 0.2)
        new_query = db.query(Movie).filter(
            Movie.overview.isnot(None),
            Movie.overview != "",
            Movie.overview != " "
        )
        if excluded_ids_list:
            new_query = new_query.filter(~Movie.movie_id.in_(excluded_ids_list))
        
        # Önce genre'e uygun filmleri al (öncelikli)
        new_with_genre = add_genre_filter(new_query)
        new_movies = new_with_genre.order_by(desc(Movie.release_date)).limit(new_count * 5).all()
        
        # Eğer yeterli film yoksa, genre'e uygun olmayanları da ekle
        if len(new_movies) < new_count * 3:
            new_without_genre = new_query.filter(
                ~or_(*[Movie.genre.ilike(f"%{genre}%") for genre in preferred_genres]) if preferred_genres else True
            ).order_by(desc(Movie.release_date)).limit((new_count * 3) - len(new_movies)).all()
            new_movies.extend(new_without_genre)
        
        # Rastgele karıştır
        random.shuffle(new_movies)
        new_movies = new_movies[:new_count * 3]  # İlk 3 katını al
        
        # Tüm aday filmleri birleştir (tekrarları kaldır)
        all_candidate_movies = {}
        for movie in popular_movies + random_movies + new_movies:
            if movie.movie_id not in all_candidate_movies:
                all_candidate_movies[movie.movie_id] = movie
        
        candidate_movies = list(all_candidate_movies.values())
        # Aday filmleri de rastgele karıştır (ek çeşitlilik için)
        random.shuffle(candidate_movies)
        
        logger.info(f"Karma strateji: {len(popular_movies)} popüler, {len(random_movies)} rastgele, {len(new_movies)} yeni = Toplam {len(candidate_movies)} aday film (rastgele karıştırıldı).")
        
        # ===== 5. PARALEL İŞLEME =====
        def process_movie(movie: Movie) -> Optional[Dict[str, Any]]:
            """Tek bir film için tahmin yapar."""
            try:
                predicted_emotions, emotion_probs, _ = recommender.predict_emotions_with_proba(
                    movie.overview,
                    auto_threshold=False,
                    custom_threshold=request.emotion_threshold
                )
                
                predicted_set = set(predicted_emotions)
                requested_set = set(request.selected_emotions)
                
                # ===== OLASILIK AĞIRLIKLI SIMILARITY HESAPLAMA =====
                if predicted_set and requested_set:
                    # 1. Jaccard Similarity (hangi duygular eşleşti)
                    intersection = len(predicted_set.intersection(requested_set))
                    union = len(predicted_set.union(requested_set))
                    jaccard_similarity = intersection / union if union > 0 else 0
                    
                    # 2. OLASILIK AĞIRLIKLI SIMILARITY (eşleşen duyguların olasılıklarının ortalaması)
                    matched_probs = [emotion_probs.get(e, 0) for e in request.selected_emotions 
                                   if e in predicted_set]
                    prob_weighted_similarity = sum(matched_probs) / len(request.selected_emotions) if matched_probs else 0
                    
                    # 3. İKİSİNİ BİRLEŞTİR (olasılık daha önemli - %70, Jaccard %30)
                    similarity = (prob_weighted_similarity * 0.7) + (jaccard_similarity * 0.3)
                else:
                    similarity = 0
                
                if similarity >= request.min_similarity_threshold:
                    # Eşleşen duyguların ortalama olasılığı (confidence için)
                    matched_probs = [emotion_probs.get(e, 0) for e in predicted_emotions 
                                   if e in request.selected_emotions]
                    avg_confidence = sum(matched_probs) / len(matched_probs) if matched_probs else 0
                    
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
                    
                    return {
                        "movie": movie,
                        "similarity_score": similarity,
                        "predicted_emotions": predicted_emotions,
                        "emotion_scores": emotion_scores,
                        "matched_emotions": list(predicted_set.intersection(requested_set)),
                        "source": "model",
                        "confidence": round(avg_confidence, 3),
                        "emotion_probs": emotion_probs
                    }
                return None
                
            except Exception as e:
                logger.warning(f"Film {movie.movie_id} için tahmin yapılamadı: {str(e)}")
                return None
        
        # Paralel işleme
        processed_count = 0
        found_count = 0
        
        # Eğer aday film yoksa, paralel işlemeyi atla
        if not candidate_movies:
            logger.info("Aday film bulunamadı, paralel işleme atlanıyor.")
        else:
            max_workers = max(1, min(6, len(candidate_movies)))  # En az 1 olmalı
            target_count = request.max_recommendations * 3
            
            logger.info(f"Paralel işleme: {max_workers} thread, {len(candidate_movies)} film...")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_movie = {
                    executor.submit(process_movie, movie): movie 
                    for movie in candidate_movies
                }
                
                for future in as_completed(future_to_movie):
                    processed_count += 1
                    result = future.result()
                    
                    if result is not None:
                        scored_movies.append(result)
                        found_count += 1
                    
                    if processed_count % 50 == 0:
                        logger.info(
                            f"İlerleme: {processed_count}/{len(candidate_movies)} film analiz edildi, "
                            f"{found_count} uygun film bulundu."
                        )
                    
                    if len(scored_movies) >= target_count:
                        logger.info(f"Yeterli film bulundu ({len(scored_movies)}), analiz durduruluyor.")
                        break
        
        elapsed_time = time.time() - start_time
        logger.info(
            f"Analiz tamamlandı: {processed_count} film işlendi, "
            f"{found_count} uygun film bulundu, toplam {len(scored_movies)} film skorlandı. "
            f"Süre: {elapsed_time:.2f} saniye."
        )
        
        # ===== 6. SKORLAMA VE SIRALAMA =====
        # Rastgele çeşitlilik faktörü (her istek için farklı) - AZALTILDI
        diversity_factor = random.uniform(-0.05, 0.05)  # -5% ile +5% arası (önceden -10% ile +10%)
        
        for rec in scored_movies:
            movie = rec["movie"]
            base_score = rec["similarity_score"]  # Artık olasılık ağırlıklı similarity
            
            rating_bonus = 0
            if movie.vote_average:
                rating_bonus = (movie.vote_average - 5.0) / 20.0
            
            # OLASILIK DEĞERLERİNE DAHA FAZLA AĞIRLIK VER
            # Confidence (ortalama olasılık) daha önemli
            confidence_bonus = rec.get("confidence", 0) * 0.3  # 0.1'den 0.3'e çıkarıldı (3 kat artırıldı)
            
            # GENRE BONUSU: Film'in genre'u seçilen duygulara uygun mu?
            genre_bonus = 0
            if preferred_genres and movie.genre:
                movie_genres = [g.strip() for g in movie.genre.split(",")] if movie.genre else []
                # Film'in genre'u ile uygun genre'lar arasında eşleşme var mı?
                matching_genres = [g for g in movie_genres if any(pref_genre.lower() in g.lower() or g.lower() in pref_genre.lower() for pref_genre in preferred_genres)]
                if matching_genres:
                    # Eşleşen genre sayısına göre bonus (max 0.15)
                    genre_bonus = min(0.15, len(matching_genres) * 0.05)
            
            # Veritabanından gelenler için küçük bonus
            database_bonus = 0.02 if rec.get("source") == "database" else 0
            
            # RASTGELE ÇEŞİTLİLİK: AZALTILDI (olasılık değerleri daha önemli)
            # (Movie ID'ye göre deterministik ama her istek için farklı)
            movie_random_factor = (hash(str(movie.movie_id) + str(random_seed)) % 100) / 1000.0  # -0.05 ile +0.05 arası (yarıya indirildi)
            
            rec["final_score"] = base_score + rating_bonus + confidence_bonus + genre_bonus + database_bonus + diversity_factor + movie_random_factor
        
        # Skorlara göre sırala
        scored_movies.sort(key=lambda x: x["final_score"], reverse=True)
        
        # İlk N filmin sırasını GÜÇLÜ bir şekilde karıştır (çeşitlilik için)
        # En yüksek skorlu filmler arasında daha fazla rastgele değişim
        if len(scored_movies) > request.max_recommendations:
            # İlk max_recommendations * 3 filmin tamamını karıştır
            top_movies = scored_movies[:request.max_recommendations * 3]
            remaining_movies = scored_movies[request.max_recommendations * 3:]
            
            # Top filmleri 3 gruba böl ve her grubu karıştır
            group_size = len(top_movies) // 3
            group1 = top_movies[:group_size]
            group2 = top_movies[group_size:group_size*2]
            group3 = top_movies[group_size*2:]
            
            # Her grubu karıştır
            random.shuffle(group1)
            random.shuffle(group2)
            random.shuffle(group3)
            
            # Grupları birleştir (biraz daha karıştır)
            top_movies = group1 + group2 + group3
            random.shuffle(top_movies[:min(request.max_recommendations * 2, len(top_movies))])  # İlk 2 katını tekrar karıştır
            
            scored_movies = top_movies + remaining_movies
        
        # ===== 7. YANITI FORMATLA =====
        recommendations = []
        for rec in scored_movies[:request.max_recommendations]:
            movie = rec["movie"]
            
            release_year = None
            if movie.release_date:
                release_year = movie.release_date.year
            
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
        
        total_time = time.time() - start_time
        logger.info(f"Toplam {len(recommendations)} öneri döndürülüyor. Süre: {total_time:.2f} saniye.")
        
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