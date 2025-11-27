"""
Kullanıcı izleme geçmişi ile ilgili Pydantic şemaları.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class HistoryCreateRequest(BaseModel):
    """İzleme geçmişi oluşturma isteği"""

    user_id: int = Field(..., description="Kullanıcı ID'si")
    movie_id: int = Field(..., description="Film ID'si")
    interaction: str = Field(
        ..., description="İnteraksiyon türü (watched, rated, liked vb.)"
    )


class HistoryItemResponse(BaseModel):
    """İzleme geçmişi öğesi yanıtı"""

    history_id: int = Field(..., description="Geçmiş ID'si")
    user_id: int = Field(..., description="Kullanıcı ID'si")
    movie_id: int = Field(..., description="Film ID'si")
    interaction: str = Field(..., description="İnteraksiyon türü")
    watch_date: datetime = Field(..., description="İzleme tarihi")

    class Config:
        from_attributes = True


class HistoryListResponse(BaseModel):
    """Kullanıcı geçmiş listesi yanıtı"""

    total: int = Field(..., description="Toplam geçmiş sayısı")
    items: List[HistoryItemResponse] = Field(..., description="Geçmiş öğeleri")



