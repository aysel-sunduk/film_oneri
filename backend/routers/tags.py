from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.auth import get_current_user
from backend.db.connection import get_db
from backend.db.models import Movie, MovieTag, User
from backend.schemas.tags import TagCreateRequest, TagResponse

router = APIRouter(tags=["Tags"])


@router.get("/tags", response_model=list[TagResponse])
def list_tags(db: Session = Depends(get_db)):
    tags = (
        db.query(MovieTag.tag)
        .distinct()
        .order_by(MovieTag.tag)
        .all()
    )
    return [TagResponse(name=t[0]) for t in tags if t[0] is not None]


@router.get("/movies/{movie_id}/tags", response_model=list[TagResponse])
def get_movie_tags(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film bulunamadı")

    tags = db.query(MovieTag).filter(MovieTag.movie_id == movie_id).all()
    return [TagResponse(name=t.tag) for t in tags if t.tag is not None]


@router.post("/movies/{movie_id}/tags", response_model=dict)
def add_movie_tag(
    movie_id: int,
    body: TagCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    movie = db.query(Movie).filter(Movie.movie_id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film bulunamadı")

    tag = MovieTag(movie_id=movie_id, tag=body.tag_name)
    db.add(tag)
    db.commit()
    return {"success": True}


