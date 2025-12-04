from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.core.auth import get_current_user
from backend.db.connection import get_db
from backend.db.models import Movie, User
from backend.schemas.movies import MovieCreate, MovieListResponse, MovieResponse, MovieUpdate

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("", response_model=MovieListResponse)
def list_movies(
    genre: Optional[str] = Query(default=None),
    year: Optional[str] = Query(default=None, alias="year"),
    limit: int = Query(default=20, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
):
    query = db.query(Movie)
    if genre:
        query = query.filter(Movie.genre.ilike(f"%{genre}%"))
    if year:
        # release_date'den yıl çıkar veya direkt yıl ile karşılaştır
        query = query.filter(Movie.release_date.like(f"{year}%"))

    total = query.count()
    items = (
        query.order_by(Movie.vote_average.desc().nullslast())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return MovieListResponse(total=total, page=page, limit=limit, items=items)


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film bulunamadı")
    return movie


@router.post("", response_model=dict)
def create_movie(
    movie_in: MovieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # İstersen User tablosuna role ekleyip admin kontrolü yapabilirsin
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
    current_user: User = Depends(get_current_user),
):
    movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film bulunamadı")

    for field, value in movie_in.dict(exclude_unset=True).items():
        setattr(movie, field, value)

    db.commit()
    return {"success": True}


@router.delete("/{movie_id}", response_model=dict)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film bulunamadı")
    db.delete(movie)
    db.commit()
    return {"success": True}

"""
@router.delete("/reset", response_model=dict)
def reset_movies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    Tüm filmleri siler (DİKKAT: Bu işlem geri alınamaz!)
    # Güvenlik için: Sadece admin kullanıcılar bu işlemi yapabilir
    # Şimdilik tüm authenticated kullanıcılar yapabilir, istersen role kontrolü ekleyebilirsin
    
    deleted_count = db.query(Movie).delete()
    db.commit()
    
    return {
        "message": "Tüm filmler silindi",
        "deleted_count": deleted_count,
        "warning": "Bu işlem geri alınamaz!"
    }

"""
