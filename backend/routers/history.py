"""
Kullanıcı izleme geçmişi endpoint'leri.
- POST /history — Yeni geçmiş kaydı (film izleme, beğenme, vb.)
- GET /history — Kullanıcının geçmişini listele
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session

from backend.core.auth import get_current_user
from backend.db.connection import get_db
from backend.db.models import Movie, User, UserHistory
from backend.schemas.history import (
    HistoryCreateRequest,
    HistoryItemResponse,
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
    Kullanıcı geçmiş kaydı oluştur (film izlendi, beğenildi, vb.)
    """
    # Kendi geçmişine ekleyebileceğini kontrol et
    if body.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sadece kendi geçmişinize kayıt ekleyebilirsiniz",
        )

    # Film var mı kontrol et
    movie = db.query(Movie).filter(Movie.movie_id == body.movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film (ID: {body.movie_id}) bulunamadı",
        )

    # Yeni geçmiş kaydı oluştur
    history = UserHistory(
        user_id=body.user_id,
        movie_id=body.movie_id,
        interaction=body.interaction,
    )
    db.add(history)
    db.commit()
    db.refresh(history)

    return {"success": True, "history_id": history.history_id}


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


@router.get("/{user_id}", response_model=HistoryListResponse)
def get_specific_user_history(
    user_id: int = Path(..., gt=0, description="Kullanıcı ID'si"),
    limit: int = Query(default=20, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Belirli bir kullanıcının geçmişini getir (kendi geçmişine erişebilir)
    """
    # Kendi geçmişine mi bakıyor kontrol et
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sadece kendi geçmişinizi görüntüleyebilirsiniz",
        )

    query = db.query(UserHistory).filter(UserHistory.user_id == user_id)
    total = query.count()

    items = (
        query.order_by(UserHistory.watch_date.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return HistoryListResponse(total=total, items=items)



