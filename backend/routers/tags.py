"""
Film etiketleri endpoint'leri.
- GET /tags — Etiketleri listele
- POST /tags — Yeni etiket ekle
- DELETE /tags/{tag_id} — Etiket sil
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session

from backend.db.connection import get_db
from backend.db.models import Movie, MovieTag
from backend.schemas.tags import TagCreateRequest, TagListResponse, TagResponse

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=TagListResponse)
def list_tags(
    movie_id: int = Query(None, description="Belirli bir filme ait etiketleri filtrele"),
    limit: int = Query(default=50, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
):
    """
    Etiketleri listele (opsiyonel olarak movie_id'ye göre filtrele)
    """
    query = db.query(MovieTag)

    if movie_id is not None:
        # Film var mı kontrol et
        movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
        if not movie:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Film (ID: {movie_id}) bulunamadı",
            )
        query = query.filter(MovieTag.movie_id == movie_id)

    total = query.count()
    items = (
        query.order_by(MovieTag.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return TagListResponse(total=total, items=items)


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_tag(
    body: TagCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Yeni etiket ekle
    """
    # Film var mı kontrol et
    movie = db.query(Movie).filter(Movie.movie_id == body.movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film (ID: {body.movie_id}) bulunamadı",
        )

    # Yeni etiket oluştur
    tag = MovieTag(
        movie_id=body.movie_id,
        tag=body.tag,
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)

    return {"success": True, "tag_id": tag.tag_id}


@router.delete("/{tag_id}", response_model=dict)
def delete_tag(
    tag_id: int = Path(..., gt=0, description="Etiket ID'si"),
    db: Session = Depends(get_db),
):
    """
    Etiketi sil
    """
    tag = db.query(MovieTag).filter(MovieTag.tag_id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Etiket (ID: {tag_id}) bulunamadı",
        )

    db.delete(tag)
    db.commit()
    return {"success": True, "message": "Etiket başarıyla silindi"}



