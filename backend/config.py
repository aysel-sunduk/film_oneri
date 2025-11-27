"""
Merkezi konfigürasyon dosyası.
Tüm ortam değişkenleri ve ayarlar burada tanımlanır.
"""

import os
from pathlib import Path
from typing import Optional

# Load environment variables from project root .env (if present)
try:
    from dotenv import load_dotenv

    project_root = Path(__file__).resolve().parents[1]
    dotenv_path = project_root / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
except Exception:
    # if python-dotenv not installed or load fails, we silently continue
    pass


class Settings:
    """Uygulama ayarları"""

    # ===== DATABASE =====
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "film_oneri")

    DATABASE_URL: str = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # ===== JWT & SECURITY =====
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "film-oneri-secret-key-change-in-production-env"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

    # ===== API =====
    API_TITLE: str = "Film Öneri API"
    API_DESCRIPTION: str = "film_oneri veritabanı üzerinde çalışan film öneri servisi"
    API_VERSION: str = "1.0.0"

    # ===== CORS =====
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # ===== ML MODELS =====
    ML_MODEL_PATH: str = os.getenv("ML_MODEL_PATH", "backend/ml/model/")

    # ===== LOGGING =====
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"


settings = Settings()
