from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from backend.core.auth import get_current_user
from backend.db.connection import get_db
from backend.db.models import Movie, User, UserHistory
from backend.schemas.history import (
    HistoryCreateRequest, 
    HistoryItemResponse,
    HistoryListResponse,
    HistoryByInteractionResponse,
    MovieInfo  # ✅ EKLENDİ
)

router = APIRouter(prefix="/history", tags=["History"])


@router.post("", response_model=dict)
def create_history_item(
    body: HistoryCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Kullanıcı geçmişine yeni bir kayıt ekler (izlendi, beğenildi, tıklandı).
    Eğer 'liked' interaction ise ve mevcut kayıt varsa, toggle mantığı ile siler (beğeniyi geri çeker).
    Diğer interaction'lar için mevcut kayıt varsa sadece watch_date güncellenir.
    """
    if body.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sadece kendi geçmişinizi güncelleyebilirsiniz",
        )

    movie = db.query(Movie).filter(Movie.movie_id == body.movie_id).first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film bulunamadı")

    # Mevcut kaydı kontrol et
    existing = db.query(UserHistory).filter(
        UserHistory.user_id == body.user_id,
        UserHistory.movie_id == body.movie_id,
        UserHistory.interaction == body.interaction
    ).first()
    
    if existing:
        # 🌟 TOGGLE MANTIĞI: Eğer 'liked' ise ve mevcut kayıt varsa, beğeniyi geri çek (sil)
        if body.interaction == "liked":
            db.delete(existing)
            db.commit()
            return {
                "success": True, 
                "message": "Beğeni geri çekildi",
                "action": "deleted",
                "is_liked": False
            }
        else:
            # Diğer interaction'lar için sadece watch_date güncelle
            existing.watch_date = datetime.utcnow()
            db.commit()
            return {
                "success": True, 
                "message": f"Geçmiş kaydı güncellendi ({body.interaction})",
                "action": "updated",
                "is_liked": True if body.interaction == "liked" else None
            }
    
    # Yeni kayıt oluştur
    history = UserHistory(
        user_id=body.user_id,
        movie_id=body.movie_id,
        interaction=body.interaction,
    )
    db.add(history)
    db.commit()
    return {
        "success": True, 
        "message": f"Geçmiş kaydı oluşturuldu ({body.interaction})",
        "action": "created",
        "is_liked": True if body.interaction == "liked" else None
    }


@router.get("/me", response_model=HistoryListResponse)
def get_my_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: Optional[int] = Query(default=100, ge=1, le=500),
    offset: Optional[int] = Query(default=0, ge=0),
):
    """
    Giriş yapan kullanıcının tüm geçmişini getirir (film bilgileri ile birlikte).
    """
    # History kayıtlarını film bilgileri ile birlikte çek
    items = (
        db.query(UserHistory, Movie)
        .join(Movie, UserHistory.movie_id == Movie.movie_id)
        .filter(UserHistory.user_id == current_user.user_id)
        .order_by(UserHistory.watch_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    # Response formatına dönüştür
    history_items = []
    for history, movie in items:
        # ✅ Movie objesini MovieInfo'ya manuel olarak dönüştür
        movie_info = MovieInfo(
            movie_id=movie.movie_id,
            title=movie.title,
            overview=movie.overview,
            release_date=movie.release_date if movie.release_date else None,  # ✅ DÜZELTME: .date() kaldırıldı
            vote_average=movie.vote_average,
            popularity=movie.popularity,
            genre=movie.genre,
            poster_url=movie.poster_url
        )
        
        history_items.append(HistoryItemResponse(
            history_id=history.history_id,
            movie_id=history.movie_id,
            interaction=history.interaction,
            watch_date=history.watch_date,
            movie=movie_info
        ))
    
    # Toplam sayı
    total = db.query(UserHistory).filter(
        UserHistory.user_id == current_user.user_id
    ).count()
    
    return HistoryListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=history_items
    )


@router.get("/me/{interaction}", response_model=HistoryByInteractionResponse)
def get_my_history_by_interaction(
    interaction: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: Optional[int] = Query(default=100, ge=1, le=500),
    offset: Optional[int] = Query(default=0, ge=0),
):
    """
    Giriş yapan kullanıcının belirli bir interaction tipine göre geçmişini getirir.
    Örnek: /history/me/viewed, /history/me/liked, /history/me/clicked
    """
    # Geçerli interaction tiplerini kontrol et
    valid_interactions = ["viewed", "liked", "clicked"]
    if interaction not in valid_interactions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz interaction tipi. Geçerli tipler: {', '.join(valid_interactions)}"
        )
    
    # History kayıtlarını film bilgileri ile birlikte çek
    items = (
        db.query(UserHistory, Movie)
        .join(Movie, UserHistory.movie_id == Movie.movie_id)
        .filter(
            UserHistory.user_id == current_user.user_id,
            UserHistory.interaction == interaction
        )
        .order_by(UserHistory.watch_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    # Response formatına dönüştür
    history_items = []
    for history, movie in items:
        # ✅ Movie objesini MovieInfo'ya manuel olarak dönüştür
        movie_info = MovieInfo(
            movie_id=movie.movie_id,
            title=movie.title,
            overview=movie.overview,
            release_date=movie.release_date if movie.release_date else None,  # ✅ DÜZELTME: .date() kaldırıldı
            vote_average=movie.vote_average,
            popularity=movie.popularity,
            genre=movie.genre,
            poster_url=movie.poster_url
        )
        
        history_items.append(HistoryItemResponse(
            history_id=history.history_id,
            movie_id=history.movie_id,
            interaction=history.interaction,
            watch_date=history.watch_date,
            movie=movie_info
        ))
    
    # Toplam sayı
    total = db.query(UserHistory).filter(
        UserHistory.user_id == current_user.user_id,
        UserHistory.interaction == interaction
    ).count()
    
    return HistoryByInteractionResponse(
        interaction=interaction,
        total=total,
        limit=limit,
        offset=offset,
        items=history_items
    )


@router.get("/{user_id}", response_model=HistoryListResponse)
def get_user_history(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: Optional[int] = Query(default=100, ge=1, le=500),
    offset: Optional[int] = Query(default=0, ge=0),
):
    """
    Belirli bir kullanıcının geçmişini getirir (sadece kendi geçmişinizi görüntüleyebilirsiniz).
    """
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sadece kendi geçmişinizi görüntüleyebilirsiniz",
        )

    # History kayıtlarını film bilgileri ile birlikte çek
    items = (
        db.query(UserHistory, Movie)
        .join(Movie, UserHistory.movie_id == Movie.movie_id)
        .filter(UserHistory.user_id == user_id)
        .order_by(UserHistory.watch_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    # Response formatına dönüştür
    history_items = []
    for history, movie in items:
        # ✅ Movie objesini MovieInfo'ya manuel olarak dönüştür
        movie_info = MovieInfo(
            movie_id=movie.movie_id,
            title=movie.title,
            overview=movie.overview,
            release_date=movie.release_date if movie.release_date else None,  # ✅ DÜZELTME: .date() kaldırıldı
            vote_average=movie.vote_average,
            popularity=movie.popularity,
            genre=movie.genre,
            poster_url=movie.poster_url
        )
        
        history_items.append(HistoryItemResponse(
            history_id=history.history_id,
            movie_id=history.movie_id,
            interaction=history.interaction,
            watch_date=history.watch_date,
            movie=movie_info
        ))
    
    # Toplam sayı
    total = db.query(UserHistory).filter(
        UserHistory.user_id == user_id
    ).count()
    
    return HistoryListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=history_items
    )


