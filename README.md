# 🎬 Film Öneri Uygulaması (Duygu Tabanlı + Hibrit)

Kullanıcının seçtiği duygulara, tür tercihlerine ve geçmiş etkileşimlerine göre **çeşitlendirilmiş** film önerileri sunan FastAPI + React uygulaması. AutoGluon ile eğitilmiş çoklu etiket duygu modelleri ve veritabanı etiketleri hibrit biçimde kullanılır.

## ✨ Öne Çıkanlar
- **Auth & Profil:** JWT, bcrypt, kayıt/giriş.
- **Duygu Tabanlı Öneri:** Seçilen mood’lara göre AutoGluon tahmini + veritabanı etiketleri.
- **Çeşitlilik:** Popüler (%30) + rastgele (%50, `func.random`) + yeni (%20), 5x fetch ve ağır karıştırma; tür önceliği (`EMOTION_GENRE_MAP`) ve olasılık ağırlıklı benzerlik (70% prob, 30% Jaccard).
- **Geçmiş Takibi:** İzle/Beğen butonları toggle; anında snackbar uyarısı; history sayfası otomatik güncellenir.
- **Kalıcı Öneriler:** Son öneriler localStorage’da saklanır, sayfa değişse de korunur.
- **Veritabanı/Kapasite:** NOT IN ID limiti (PostgreSQL param sınırı), boş adaylarda güvenli `max_workers`.

## 📁 Yapı (özet)
```
backend/   FastAPI, SQLAlchemy, AutoGluon modelleri
  app.py, config.py
  routers/ (auth, movies, history, recommendation, tags, ratings)
  ml/      (automl_train.py, modeller predictor_*)
  db/      (connection, models, sql)
frontend/  React 19 + Vite + MUI
  src/pages (Home, MoodSelection, RecommendedMovies, MovieDetail, UserHistory, ...)
  src/components (MovieCard, Navbar)
  src/api (api.js, history.js, client.js)
README.md (bu dosya)
run_api.bat (Windows backend başlatma)
```

## 🚀 Kurulum
### Gereksinimler
- Python 3.10+ (AutoML için 3.10–3.12 önerilir)
- Node.js 18+
- PostgreSQL 12+

### Backend
```bash
cd backend
pip install -r requirements.txt
# AutoML eğitim/evaluasyon için ek paketler:
# pip install -r requirements_automl.txt

# Ortam değişkenleri (örn.)
setx DB_USER "postgres"
setx DB_PASSWORD "your_pass"
setx DB_HOST "localhost"
setx DB_PORT "5432"
setx DB_NAME "film_oneri"

uvicorn app:app --reload  # http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
```

## 🧠 ML / AutoML
- Araç: **AutoGluon Tabular** (1.4.0), çoklu etiket duygu sınıflandırması.
- Veri: `movies` + `emotions` join; 8 duygu etiketi (mutlu, üzgün, stresli, motive, romantik, heyecanlı, nostaljik, rahat).
- Özellikler: `overview` metni n‑gram + metin istatistikleri; OOM riskine karşı vocab küçültme.
- Modeller: `backend/ml/model/predictor_*` klasörlerinde saklanır; `automl_train.py` ana eğitim dosyası. Değerlendirme için ayrı notebook kullanıldı (ana modeli bozmaz).

## 🔌 API Uçları (seçme)
- `POST /auth/register`, `POST /auth/login`
- `GET /movies`, `GET /movies/search`, `GET /movies/{id}`
- `POST /recommendations` (duygu + tür + geçmiş filtreleri; çeşitlendirme)
- `POST /history` (izle/beğen toggle, user_id backend’de kimlikten alınır)
- Swagger: `http://localhost:8000/docs`

## 🧭 Öneri Mantığı (kısa)
- Kategori payı: popüler %30, rastgele %50 (PostgreSQL `func.random()`), yeni %20.
- Tür uyumu: `EMOTION_GENRE_MAP` ile önceliklendirme, genre bonus skoru.
- Benzerlik: Olasılık ağırlıklı (70%) + Jaccard (30%), güven bonusu; çeşitlilik faktörü.
- Performans: NOT IN için param limiti 1000; boş adayda paralel işleme kapalı; `max_workers` ≥ 1.

## 🖥️ Frontend Davranışları
- `MovieCard`: İzle/Beğen toggle, her tıklamada API; snackbar uyarıları; `onHistoryChange` ile history sayfasını canlı günceller.
- `UserHistory`: Item silinince listeden anında düşer, eklenince yeniden fetch eder.
- `RecommendedMovies`: Son öneriler localStorage’da tutulur; sayfa değişse de gösterilir.

## 🧪 Test / Geliştirme
```bash
# Backend test
cd backend && pytest -v
# Format
black backend/
# Lint
flake8 backend/
```

## 📄 Lisans ve İletişim
- Lisans: MIT
- Geliştirici: Aysel Sündük,Tuğba Sümen
- Kaynak repo: https://github.com/aysel-sunduk/film_oneri
