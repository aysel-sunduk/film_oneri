from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Movie(Base):
    __tablename__ = "movies"

    # Primary key
    movie_id = Column(Integer, primary_key=True, index=True)
    
    # Dataset kolonları (tam eşleşme)
    title = Column(String(255), nullable=False, index=True)  # Title
    release_date = Column(Date, nullable=True)   # Release_Date (DATE olarak da saklanabilir)
    overview = Column(Text, nullable=False)  # Overview
    popularity = Column(Float, index=True)  # Popularity
    vote_count = Column(Integer, index=True)  # Vote_Count
    vote_average = Column(Float, index=True)  # Vote_Average
    original_language = Column(String(10), default='en', index=True)  # Original_Language
    genre = Column(String(255), index=True)  # Genre
    poster_url = Column(Text)  # Poster_Url
    
    # Sistem kolonları
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


