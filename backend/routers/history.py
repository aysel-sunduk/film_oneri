"""
Kullanıcı izleme geçmişi endpoint'leri.
- POST /history — Yeni geçmiş kaydı (film izleme, beğenme, vb.)
- GET /history — Kullanıcının geçmişini listele
"""

from datetime import datetime  # ✅ BUNU EKLE!
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.core.auth import get_current_user
from backend.db.connection import get_db
from backend.db.models import Movie, User, UserHistory
from backend.schemas.history import (
    HistoryCreateRequest,
    HistoryListResponse,
)

router = APIRouter(prefix="/history", tags=["History"])

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_history_item(
    body: HistoryCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Kullanıcı geçmiş kaydı oluştur veya güncelle
    """
    # Film var mı kontrol et
    movie_exists = db.query(Movie.movie_id).filter(Movie.movie_id == body.movie_id).first()
    if not movie_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film (ID: {body.movie_id}) bulunamadı"
        )

    # Aynı kayıt var mı kontrol et (user + movie + interaction aynıysa)
    existing_history = db.query(UserHistory).filter(
        UserHistory.user_id == current_user.user_id,
        UserHistory.movie_id == body.movie_id,
        UserHistory.interaction == body.interaction
    ).first()

    if existing_history:
        # ✅ VARSA: Tarihi güncelle (yeniden izlendi/beğenildi)
        existing_history.watch_date = datetime.utcnow()
        db.commit()
        db.refresh(existing_history)
        return {
            "success": True, 
            "history_id": existing_history.history_id, 
            "action": "updated",
            "message": "Mevcut kayıt güncellendi"
        }
    else:
        # ✅ YOKSA: Yeni kayıt oluştur
        history = UserHistory(
            user_id=current_user.user_id,
            movie_id=body.movie_id,
            interaction=body.interaction,
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        return {
            "success": True, 
            "history_id": history.history_id, 
            "action": "created",
            "message": "Yeni kayıt oluşturuldu"
        }

@router.get("", response_model=HistoryListResponse)
def get_user_history(
    limit: int = Query(default=20, ge=1, le=100, description="Kaç kayıt gösterilsin"),
    page: int = Query(default=1, ge=1, description="Sayfa numarası"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mevcut kullanıcının izleme geçmişini getir (sayfalandırılmış)
    """
    query = db.query(UserHistory).filter(UserHistory.user_id == current_user.user_id)

    # Toplam sayı
    total = query.count()

    # Sayfalandırma (en yeni ilk)
    items = (
        query.order_by(UserHistory.watch_date.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return HistoryListResponse(total=total, items=items)