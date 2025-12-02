from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.connection import init_db
from backend.routers import auth, history, movies, recommendation, tags

app = FastAPI(
    title="Film Öneri API",
    description="film_oneri veritabanı üzerinde çalışan film öneri servisi",
    version="1.0.0",
)

# CORS – frontend'ten istek atabilmek için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # prod'da domain bazlı kısıtla
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Veritabanı tablolarını oluştur (varsa dokunmaz)
    init_db()


# Router'ları ekle
app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(history.router)
app.include_router(recommendation.router)
app.include_router(tags.router)


