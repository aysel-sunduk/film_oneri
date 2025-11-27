"""
Film etiketleri ile ilgili Pydantic şemaları.
"""

from typing import List

from pydantic import BaseModel, Field


class TagResponse(BaseModel):
    """Etiket yanıtı"""

    tag_id: int = Field(..., description="Etiket ID'si")
    tag: str = Field(..., description="Etiket adı")


class TagCreateRequest(BaseModel):
    """Etiket oluşturma isteği"""

    movie_id: int = Field(..., description="Film ID'si")
    tag: str = Field(..., min_length=1, max_length=50, description="Etiket adı")


class TagListResponse(BaseModel):
    """Etiket listesi yanıtı"""

    total: int = Field(..., description="Toplam etiket sayısı")
    items: List[TagResponse] = Field(..., description="Etiketler")



