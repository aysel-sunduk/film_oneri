"""
Film yönetimi endpoint'leri.
- GET /movies — Film listesi (sayfalandırılmış, filtreleme)
- GET /movies/{id} — Film detayları
- POST /movies — Yeni film ekle (admin)
- PUT /movies/{id} — Film güncelle (admin)
- DELETE /movies/{id} — Film sil (admin)
- GET /movies/search — Film arama
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session

from backend.db.connection import get_db
from backend.db.models import Movie
from backend.schemas.movies import (
    MovieCreate,
    MovieListResponse,
    MovieResponse,
    MovieUpdate,
)

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("", response_model=MovieListResponse)
def list_movies(
    genre: Optional[str] = Query(
        default=None, description="Film türü filtrelemesi (örn: Action)"
    ),
    year: Optional[str] = Query(
        default=None, description="Yayın yılı filtrelemesi"
    ),
    min_rating: Optional[float] = Query(
        default=None, ge=0, le=10, description="Minimum IMDb puanı"
    ),
    limit: int = Query(
        default=20, ge=1, le=100, description="Sayfa başına öğe sayısı"
    ),
    page: int = Query(default=1, ge=1, description="Sayfa numarası"),
    sort_by: str = Query(
        default="rating", description="Sıralama: rating, year, title"
    ),
    db: Session = Depends(get_db),
):
    """
    Film listesi (sayfalandırılmış, filtreleme ve sıralama destekli)
    """
    query = db.query(Movie)

    # Filtreleme
    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))
    if year:
        query = query.filter(Movie.released_year == year)
    if min_rating is not None:
        query = query.filter(Movie.imdb_rating >= min_rating)

    # Toplam sayı
    total = query.count()

    # Sıralama
    if sort_by == "rating":
        query = query.order_by(Movie.imdb_rating.desc().nullslast())
    elif sort_by == "year":
        query = query.order_by(Movie.released_year.desc())
    elif sort_by == "title":
        query = query.order_by(Movie.series_title.asc())

    # Sayfalandırma
    items = (
        query.offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return MovieListResponse(total=total, page=page, limit=limit, items=items)


@router.get("/search", response_model=MovieListResponse)
def search_movies(
    q: str = Query(..., min_length=1, description="Arama sorgusu (film adı, yönetmen, oyuncu)"),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Film arama — film adı, yönetmen veya oyuncu ismine göre
    """
    search_pattern = f"%{q}%"
    query = db.query(Movie).filter(
        (Movie.series_title.ilike(search_pattern))
        | (Movie.director.ilike(search_pattern))
        | (Movie.star1.ilike(search_pattern))
        | (Movie.star2.ilike(search_pattern))
        | (Movie.star3.ilike(search_pattern))
        | (Movie.star4.ilike(search_pattern))
    )

    total = query.count()
    items = query.limit(limit).all()

    return MovieListResponse(total=total, page=1, limit=limit, items=items)


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(
    movie_id: int = Path(..., gt=0, description="Film ID'si"),
    db: Session = Depends(get_db),
):
    """
    Film detaylarını getir
    """
    movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film (ID: {movie_id}) bulunamadı",
        )
    return movie


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_movie(
    movie_in: MovieCreate,
    db: Session = Depends(get_db),
):
    """
    Yeni film ekle (admin tarafından)
    """
    movie = Movie(**movie_in.dict())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return {"success": True, "movie_id": movie.movie_id}


@router.put("/{movie_id}", response_model=dict)
def update_movie(
    movie_id: int,
    movie_in: MovieUpdate,
    db: Session = Depends(get_db),
):
    """
    Film bilgilerini güncelle
    """
    movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film (ID: {movie_id}) bulunamadı",
        )

    # Sadece gönderilen alanları güncelle
    for field, value in movie_in.dict(exclude_unset=True).items():
        setattr(movie, field, value)

    db.commit()
    return {"success": True, "message": "Film başarıyla güncellendi"}


@router.delete("/{movie_id}", response_model=dict)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
):
    """
    Film sil (admin tarafından)
    """
    movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film (ID: {movie_id}) bulunamadı",
        )
    db.delete(movie)
    db.commit()
    return {"success": True, "message": "Film başarıyla silindi"}



