"""
FastAPI ana uygulaması — Film Öneri Sistemi

Tüm router'ları ve middleware'leri burada entegre ediyoruz.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.db.connection import init_db
from backend.routers import auth, history, movies, recommendation, tags

# FastAPI uygulaması oluştur
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
)

# CORS middleware — frontend'ten API çağrıları yapabilmek için
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


@app.on_event("startup")
def on_startup():
    """Uygulama başlangıcında veritabanı tablolarını oluştur"""
    init_db()


# Routers'ı ekle
app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(history.router)
app.include_router(recommendation.router)
app.include_router(tags.router)


@app.get("/", tags=["Health"])
def root():
    """Sağlık kontrolü endpoint'i"""
    return {
        "message": "Film Öneri API'ye hoş geldiniz!",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """API sağlık durumu kontrolü"""
    return {"status": "ok", "api": "film-oneri"}



