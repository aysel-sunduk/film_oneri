"""
Veritabanı bağlantısı ve oturum yönetimi.
PostgreSQL ile SQLAlchemy ORM kullanılmaktadır.
"""

import os

# SQLAlchemy C extension'ları Python 3.12 ile sorun çıkardığı için
# program içinden devre dışı bırakıyoruz.
os.environ.setdefault("SQLALCHEMY_DISABLE_CEXT", "1")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import settings
from backend.db.models import Base
from sqlalchemy.exc import OperationalError
import sys

# Engine ve SessionLocal oluştur
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Veritabanı tablolarını oluşturur (varsa zaten bırakır)."""
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        # Daha anlaşılır bir hata mesajı göster
        host = getattr(settings, "DB_HOST", "localhost")
        port = getattr(settings, "DB_PORT", "5432")
        user = getattr(settings, "DB_USER", "<user>")
        dbname = getattr(settings, "DB_NAME", "<db>")
        err_msg = (
            "Veritabanına bağlanılamadı. Lütfen .env veya çevresel değişkenleri kontrol edin\n"
            f"Bağlantı denendi: host={host} port={port} user={user} db={dbname}\n"
            f"Hata: {e}"
        )
        print(err_msg, file=sys.stderr)
        raise


def get_db():
    """Her istek için veritabanı session'ı üretir."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



