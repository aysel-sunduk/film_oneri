from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Movie(Base):
    __tablename__ = "movies"

    movie_id = Column(Integer, primary_key=True, index=True)
    series_title = Column(String(255), nullable=False)
    released_year = Column(String(10))
    genre = Column(String(255))
    imdb_rating = Column(Float)
    meta_score = Column(Integer)
    overview = Column(Text, nullable=False)
    director = Column(String(255))
    star1 = Column(String(255))
    star2 = Column(String(255))
    star3 = Column(String(255))
    star4 = Column(String(255))
    duration = Column(Integer)
    language = Column(String(50))
    country = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    emotions = relationship("Emotion", back_populates="movie", cascade="all, delete-orphan")
    tags = relationship("MovieTag", back_populates="movie", cascade="all, delete-orphan")
    histories = relationship("UserHistory", back_populates="movie", cascade="all, delete-orphan")


class Emotion(Base):
    __tablename__ = "emotions"

    emotion_id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.movie_id", ondelete="CASCADE"))
    emotion_label = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    movie = relationship("Movie", back_populates="emotions")


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    mood = Column(String(50))
    preferred_genre = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    histories = relationship("UserHistory", back_populates="user", cascade="all, delete-orphan")


class UserHistory(Base):
    __tablename__ = "user_history"

    history_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    movie_id = Column(Integer, ForeignKey("movies.movie_id", ondelete="CASCADE"))
    interaction = Column(String(50))
    watch_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="histories")
    movie = relationship("Movie", back_populates="histories")


class MovieTag(Base):
    __tablename__ = "movie_tags"

    tag_id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.movie_id", ondelete="CASCADE"))
    tag = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    movie = relationship("Movie", back_populates="tags")


