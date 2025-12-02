"""
Merkezi konfigürasyon dosyası.
Tüm ortam değişkenleri ve ayarlar burada tanımlanır.
"""

import os
from pathlib import Path
from typing import List, Optional

# Load environment variables from project root .env (if present)
try:
    from dotenv import load_dotenv

    # __file__ in 2 üst dizini (proje kökü) bul
    project_root = Path(__file__).resolve().parents[1]
    dotenv_path = project_root / ".env"
    if dotenv_path.exists():
        # .env dosyasındaki değişkenleri environment'a yükle
        load_dotenv(dotenv_path)
        print(f"✅ .env dosyası yüklendi: {dotenv_path}")
    else:
        print(f"⚠️  .env dosyası bulunamadı: {dotenv_path}")
except Exception as e:
    # python-dotenv kurulu değilse veya yükleme başarısız olursa sessizce devam et
    print(f"ℹ️  .env yüklenemedi: {e}")


class Settings:
    """
    Uygulama ayarları.
    Tüm değerler os.environ aracılığıyla environment değişkenlerinden okunur.
    """

    # ===== DATABASE =====
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")

    # DATABASE_URL doğrudan env'den ayarlanabilir, aksi takdirde bileşenlerden oluşturulur
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # ===== JWT & SECURITY =====
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # ===== API =====
    API_TITLE: str = os.getenv("API_TITLE", "Film Öneri API")
    API_DESCRIPTION: str = os.getenv("API_DESCRIPTION", "film_oneri veritabanı üzerinde çalışan film öneri servisi")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")

    # ===== CORS =====
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # ===== ML MODELS =====
    ML_MODEL_PATH: str = os.getenv("ML_MODEL_PATH", "backend/ml/model")
    
    # ML Model dosya yolları - AutoGluon için
    MODEL_PATH: Path = Path(ML_MODEL_PATH)
    
    # Eski model dosyaları (TF-IDF + tek model)
    TFIDF_PATH: str = str(MODEL_PATH / "tfidf_vectorizer.pkl")
    BEST_MODEL_PATH: str = str(MODEL_PATH / "best_model.pkl")
    LABEL_ENCODER_PATH: str = str(MODEL_PATH / "label_encoder.pkl")
    
    # AutoGluon model dosyaları (YENİ)
    MULTI_LABEL_BINARIZER_PATH: str = str(MODEL_PATH / "multi_label_binarizer.pkl")
    
    # AutoGluon model kullanım modu
    USE_AUTOGLUON: bool = os.getenv("USE_AUTOGLUON", "true").lower() == "true"
    
    # ===== EMOTION CATEGORIES =====
    EMOTION_CATEGORIES: List[str] = [
        "mutlu", "üzgün", "stresli", "motive", "romantik", 
        "heyecanlı", "nostaljik", "rahat"
    ]
    
    # Duygu -> Tür Eşleştirmesi
    EMOTION_GENRE_MAP: dict = {
        "mutlu": ["Comedy", "Animation", "Family", "Musical"],
        "üzgün": ["Drama", "Romance", "War"],
        "stresli": ["Comedy", "Animation", "Family"],
        "motive": ["Biography", "Sport", "Action", "Adventure"],
        "romantik": ["Romance", "Drama", "Comedy"],
        "heyecanlı": ["Action", "Thriller", "Adventure", "Sci-Fi"],
        "nostaljik": ["Drama", "History", "War", "Western"],
        "rahat": ["Comedy", "Animation", "Family", "Fantasy"]
    }

    # ===== LOGGING =====
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # ===== RECOMMENDATION SETTINGS =====
    DEFAULT_MAX_RECOMMENDATIONS: int = int(os.getenv("DEFAULT_MAX_RECOMMENDATIONS", "10"))
    MIN_SIMILARITY_THRESHOLD: float = float(os.getenv("MIN_SIMILARITY_THRESHOLD", "0.3"))
    PREDICTION_BATCH_SIZE: int = int(os.getenv("PREDICTION_BATCH_SIZE", "50"))

    def __init__(self):
        """Ayarları başlatır ve gerekli kontrolleri yapar."""
        self._validate_settings()

    def _validate_settings(self):
        """Gerekli ayarları kontrol eder."""
        required_settings = [
            "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"
        ]
        
        missing = []
        for setting in required_settings:
            value = getattr(self, setting)
            if not value:
                missing.append(setting)
        
        if missing:
            print(f"⚠️  UYARI: Aşağıdaki ayarlar eksik veya boş: {missing}")
            print("   Lütfen .env dosyasını kontrol edin.")
        
        # AutoGluon model yolu kontrolü
        if self.USE_AUTOGLUON:
            model_dir = Path(self.ML_MODEL_PATH)
            if not model_dir.exists():
                print(f"⚠️  UYARI: Model klasörü bulunamadı: {model_dir}")
                print("   Lütfen önce modeli eğitin: python -m ml.automl_train")
            else:
                # MultiLabelBinarizer dosyasını kontrol et
                binarizer_path = model_dir / "multi_label_binarizer.pkl"
                if not binarizer_path.exists():
                    print(f"⚠️  UYARI: MultiLabelBinarizer dosyası bulunamadı: {binarizer_path}")


settings = Settings()