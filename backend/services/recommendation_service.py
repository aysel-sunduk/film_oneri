"""
Öneri ve duygu tahmini servis katmanı.
- Ruh haliye (mood) göre kişiselleştirilmiş film önerileri
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
    
    Strateji:
    1. Kullanıcının daha önce izledikleri filmleri hariç tut
    2. İsterse mood (duygu) filtresi uygula → emotions tablosundan eşleştir
    3. İsterse genre filtresi uygula
    4. IMDB puanına göre sıralanmış sonuç döndür
    
    Args:
        db: SQLAlchemy Session
        user_id: Kullanıcı ID'si
        mood: Opsiyonel mood filtresi (örn: happy, sad, dramatic)
        genre: Opsiyonel genre filtresi
        limit: Kaç film önerilsin (max 50)
    
    Returns:
        Önerilen filmler listesi (dict formatında)
    """
    # Başlangıç sorgusu
    query = db.query(Movie)

    # 1. Kullanıcının izledikleri filmleri hariç tut
    watched_ids = (
        db.query(UserHistory.movie_id)
        .filter(UserHistory.user_id == user_id)
        .subquery()
    )
    query = query.filter(Movie.movie_id.notin_(watched_ids))

    # 2. Mood filtrelemesi (emotions tablosundan)
    if mood:
        emotion_movie_ids = (
            db.query(Emotion.movie_id)
            .filter(Emotion.emotion_label.ilike(f"%{mood}%"))
            .subquery()
        )
        query = query.filter(Movie.movie_id.in_(emotion_movie_ids))

    # 3. Genre filtrelemesi
    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))

    # 4. IMDB puanına göre sıralama (yüksekten düşüğe)
    movies = (
        query.order_by(Movie.imdb_rating.desc().nullslast())
        .limit(limit)
        .all()
    )

    # 5. Sonuçları formatla (emotion label ekleyerek)
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
    
    İki yöntem:
    1. movie_id varsa: Emotion tablosundan etiketi getirir
    2. overview varsa: (İleride) ML modeliyle tahminde bulunur
    
    Args:
        db: SQLAlchemy Session
        movie_id: Opsiyonel film ID'si
        overview: Opsiyonel film açıklaması
    
    Returns:
        {
            "movie_id": int | None,
            "emotion_label": str
        }
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

    # Eğer sadece overview verilmişse, ML modeliyle tahmin yap
    # TODO: Gerçek ML modelini entegre et (AutoML / fine-tuned NLP)
    # Şimdilik placeholder:
    if overview:
        # Basit heuristic (demo amaçlı)
        overview_lower = overview.lower()
        if any(word in overview_lower for word in ["happy", "joy", "love", "cheerful"]):
            predicted_label = "happy"
        elif any(word in overview_lower for word in ["sad", "tragic", "death", "loss"]):
            predicted_label = "sad"
        elif any(word in overview_lower for word in ["dark", "horror", "scary"]):
            predicted_label = "dark"
        elif any(word in overview_lower for word in ["action", "fight", "battle", "exciting"]):
            predicted_label = "exciting"
        else:
            predicted_label = "dramatic"
        
        return {"movie_id": None, "emotion_label": predicted_label}

    return {"movie_id": None, "emotion_label": "unknown"}



