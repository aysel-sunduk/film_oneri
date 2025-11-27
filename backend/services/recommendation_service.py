"""
Öneri ve duygu tahmini servis katmanı.
- Ruh haline (mood) göre kişiselleştirilmiş film önerileri
- Emotion tablosundan duygu etiketi getirme
- ML modeliyle duygu tahmini
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.db.models import Emotion, Movie, UserHistory


def get_recommendations_for_user(
    db: Session,
    user_id: int,
    mood: Optional[str] = None,
    genre: Optional[str] = None,
    limit: int = 10,
) -> List[dict]:
    """
    Kullanıcıya kişiselleştirilmiş film önerileri sunar.
    """
    # Başlangıç sorgusu
    query = db.query(Movie)

    # 1. Kullanıcının izledikleri filmleri hariç tut
    watched_ids = db.query(UserHistory.movie_id).filter(
        UserHistory.user_id == user_id
    )
    watched_ids_list = [id[0] for id in watched_ids.all() if id[0] is not None]
    
    if watched_ids_list:
        query = query.filter(Movie.movie_id.notin_(watched_ids_list))

    # 2. Mood filtrelemesi (emotions tablosundan)
    if mood:
        # Mood'u Türkçe'den İngilizce'ye çevir (emotions tablosu İngilizce olabilir)
        mood_mapping = {
            "mutlu": "happy",
            "hüzünlü": "sad", 
            "heyecanlı": "exciting",
            "rahat": "relaxed",
            "sakin": "calm"
        }
        
        english_mood = mood_mapping.get(mood.lower(), mood.lower())
        
        emotion_movie_ids = db.query(Emotion.movie_id).filter(
            Emotion.emotion_label.ilike(f"%{english_mood}%")
        )
        emotion_ids_list = [id[0] for id in emotion_movie_ids.all() if id[0] is not None]
        
        if emotion_ids_list:
            query = query.filter(Movie.movie_id.in_(emotion_ids_list))

    # 3. Genre filtrelemesi
    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))

    # 4. IMDB puanına göre sıralama (yüksekten düşüğe)
    movies = (
        query.order_by(Movie.imdb_rating.desc().nullslast())
        .limit(limit)
        .all()
    )

    # 5. Sonuçları formatla
    results: List[dict] = []
    for m in movies:
        # Her film için emotion etiketi bul
        emotion = (
            db.query(Emotion)
            .filter(Emotion.movie_id == m.movie_id)
            .order_by(Emotion.created_at.desc())
            .first()
        )
        
        results.append(
            {
                "movie_id": m.movie_id,
                "series_title": m.series_title,
                "genre": m.genre or "",
                "imdb_rating": m.imdb_rating or 0.0,
                "overview": m.overview or "",
                "poster_link": getattr(m, 'poster_link', None),
                "emotion_label": emotion.emotion_label if emotion else None,
            }
        )

    return results


def predict_emotion_for_movie(
    db: Session,
    movie_id: Optional[int] = None,
    overview: Optional[str] = None,
) -> dict:
    """
    Film açıklamasından duygu tahmini yapar.
    """
    if movie_id is not None:
        # Emotion tablosundan tahmini duygu etiketini al
        emotion = (
            db.query(Emotion)
            .filter(Emotion.movie_id == movie_id)
            .order_by(Emotion.created_at.desc())
            .first()
        )
        label = emotion.emotion_label if emotion else "unknown"
        return {"movie_id": movie_id, "emotion_label": label}

    # Eğer sadece overview verilmişse, basit tahmin yap
    if overview:
        overview_lower = overview.lower()
        
        # Türkçe ve İngilizce kelimelerle kontrol
        if any(word in overview_lower for word in ["happy", "joy", "love", "cheerful", "mutlu", "neşe", "aşk"]):
            predicted_label = "happy"
        elif any(word in overview_lower for word in ["sad", "tragic", "death", "loss", "hüzünlü", "trajik", "ölüm"]):
            predicted_label = "sad"
        elif any(word in overview_lower for word in ["action", "fight", "battle", "exciting", "heyecanlı", "aksiyon", "savaş"]):
            predicted_label = "exciting"
        elif any(word in overview_lower for word in ["relax", "peaceful", "calm", "rahat", "sakin", "huzurlu"]):
            predicted_label = "relaxed"
        else:
            predicted_label = "dramatic"
        
        return {"movie_id": None, "emotion_label": predicted_label}

    return {"movie_id": None, "emotion_label": "unknown"}