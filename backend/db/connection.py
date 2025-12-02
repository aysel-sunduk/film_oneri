import os
from typing import Generator
import logging

# SQLAlchemy C extension'ları Python 3.12 ile sorun çıkardığı için
# program içinden devre dışı bırakıyoruz.
os.environ.setdefault("SQLALCHEMY_DISABLE_CEXT", "1")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# ÖNEMLİ: config.py'yi import etmek .env dosyasını yükler
from backend.config import settings
from backend.db.models import Base

# Logging setup
logger = logging.getLogger(__name__)

# =====================================================
# Veritabanı Bağlantı Bilgileri
# =====================================================

# Config'den DATABASE_URL'i al
DATABASE_URL = settings.DATABASE_URL

logger.info(f"Veritabanı bağlantısı kuruluyor: {DATABASE_URL.replace(settings.DB_PASSWORD, '***')}")

try:
    # SQLAlchemy Motorunu (Engine) oluştur
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Bağlantı sağlığını kontrol et
        echo=settings.DEBUG   # Debug modunda SQL sorgularını göster
    )

    # SQLAlchemy Oturum Yapıcısını (Sessionmaker) oluştur
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    logger.info("✅ Veritabanı motoru başarıyla oluşturuldu")

except Exception as e:
    logger.error(f"❌ Veritabanı motoru oluşturulamadı: {e}")
    raise

# --- Veritabanı Fonksiyonları ---

def init_db() -> None:
    """
    Model tanımlarıyla uyumlu veritabanı tablolarını oluşturur 
    (tablolar zaten varsa bırakır).
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Veritabanı tabloları başarıyla oluşturuldu/doğrulandı")
    except SQLAlchemyError as e:
        logger.error(f"❌ Veritabanı tabloları oluşturulamadı: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Her istek için veritabanı session'ı (oturum) üretir ve kullanımdan sonra kapatır.
    FastAPI Bağımlılık Enjeksiyonu için tasarlanmıştır.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"❌ Veritabanı oturumu hatası: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    ML script'leri veya bağımsız kullanımlar için doğrudan bir session nesnesi döndürür 
    (context manager/generator DEĞİL).
    Session'ı kullanımdan sonra manuel olarak kapatmayı UNUTMAYIN.
    
    Kullanım:
    ```python
    db = get_db_session()
    try:
        # veritabanı işlemleri
    finally:
        db.close()
    ```
    """
    return SessionLocal()


def test_connection() -> bool:
    """
    Veritabanı bağlantısını test eder.
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✅ Veritabanı bağlantı testi başarılı")
        return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Veritabanı bağlantı testi başarısız: {e}")
        return False