# Film Öneri Projesi - Dosya Yapısı İskeleti

## 📁 Proje Genel Yapısı

```
Film_oneri/
├── imdb_top_1000.csv                 # Film veri seti (1000 film)
├── backend/                          # FastAPI uygulaması
│   ├── __init__.py
│   ├── app.py                        # Ana uygulama ve router'lar
│   ├── config.py                     # Konfigürasyon (şu an boş)
│   ├── requirements.txt              # Python bağımlılıkları
│   ├── __pycache__/
│   │
│   ├── core/
│   │   └── auth.py                   # Kimlik doğrulama işlemleri (token, hash, şifre)
│   │
│   ├── db/
│   │   ├── connection.py             # PostgreSQL bağlantısı ve oturum yönetimi
│   │   ├── models.py                 # SQLAlchemy ORM modelleri (Movie, User, Emotion, vb.)
│   │   ├── film_oneri.sql            # SQL şeması (tablo oluşturma komutları)
│   │   ├── database.ipynb            # Jupyter notebook (veri keşif/test)
│   │   └── __pycache__/
│   │
│   ├── ml/
│   │   ├── automl_train.py           # Modeli eğitme (AutoML)
│   │   ├── preprocess.py             # Veri ön işleme (normalization, encoding)
│   │   └── model/                    # Eğitilmiş model dosyaları
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py                   # POST /auth/register, /auth/login, /auth/profile
│   │   ├── movies.py                 # GET /movies/{id}, /movies/search
│   │   ├── history.py                # GET/POST /history (izleme geçmişi)
│   │   ├── recommendation.py         # POST /recommend (film önerileri)
│   │   └── tags.py                   # GET/POST /tags (etiketler)
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                   # Pydantic models (RegisterRequest, LoginRequest, vb.)
│   │   ├── movies.py                 # Film veri modelleri
│   │   ├── history.py                # İzleme geçmişi şemaları
│   │   ├── recommendation.py         # Öneri isteği/yanıtı şemaları
│   │   └── tags.py                   # Etiket şemaları
│   │
│   ├── services/
│   │   ├── automl_predict.py         # Önceden eğitilmiş modeli kullanarak tahmin
│   │   ├── recommendation_service.py # Öneri algoritması mantığı
│   │   └── recommender.py            # Öneri motoru (ML modeliyle entegrasyon)
│   │
│   └── utils/
│       └── helpers.py                # Yardımcı fonksiyonlar (validasyon, formatlama)
│
└── frontend/                         # React + Vite uygulaması
    ├── index.html                    # Ana HTML dosyası
    ├── package.json                  # NPM bağımlılıkları (React, MUI, React Router)
    ├── vite.config.js                # Vite yapılandırması
    ├── eslint.config.js              # ESLint kuralları
    ├── README.md
    │
    ├── public/                       # Statik dosyalar (favicon, logosu vb.)
    │
    └── src/
        ├── main.jsx                  # React başlangıç noktası
        ├── App.jsx                   # Ana uygulama bileşeni (yönlendirme)
        ├── App.css                   # Global stiller
        ├── index.css                 # Genel CSS
        ├── theme.js                  # Material-UI tema yapılandırması
        │
        ├── api/
        │   └── client.js             # Axios/Fetch istemci (API çağrıları)
        │
        ├── components/
        │   ├── Navbar.jsx            # Navigasyon çubuğu
        │   └── MovieCard.jsx         # Film kartı bileşeni
        │
        ├── pages/
        │   ├── Login.jsx             # Giriş sayfası
        │   ├── Register.jsx          # Kayıt sayfası
        │   ├── MoodSelection.jsx     # Ruh hali seçim sayfası
        │   ├── RecommendedMovies.jsx # Önerilen filmler sayfası
        │   ├── MovieDetail.jsx       # Film detay sayfası
        │   └── UserHistory.jsx       # Kullanıcı izleme geçmişi
        │
        ├── data/
        │   └── mockData.js           # Test ve geliştirme için örnek veriler
        │
        └── assets/                   # Görseller, ikonlar vb.
```

---

## 🔧 Temel Teknolojiler

### Backend
- **Framework**: FastAPI
- **Veritabanı**: PostgreSQL (SQLAlchemy ORM)
- **Kimlik Doğrulama**: JWT Token + bcrypt (password hashing)
- **ML**: AutoML (tahmin modeli)
- **Dependencies**: uvicorn, python-jose, passlib, psycopg2-binary

### Frontend
- **Framework**: React 19
- **UI Library**: Material-UI (MUI v7)
- **Routing**: React Router v7
- **Build Tool**: Vite
- **Styling**: Emotion (CSS-in-JS)

---

## 📋 Veritabanı Modelleri (SQLAlchemy)

### Movie
- `movie_id` (PK)
- `series_title`, `released_year`, `genre`
- `imdb_rating`, `meta_score`
- `overview`, `director`
- `star1`, `star2`, `star3`, `star4`
- `duration`, `language`, `country`
- `created_at`
- İlişkiler: `emotions`, `tags`, `histories`

### User
- `user_id` (PK)
- `username`, `email` (unique)
- `password_hash`
- `mood`, `preferred_genre`
- İlişkiler: `histories`

### Emotion
- `emotion_id` (PK)
- `movie_id` (FK → Movie)
- `emotion_label`
- İlişkiler: `movie`

### MovieTag
- Taglama sistemi

### UserHistory
- Kullanıcının izleme/etkileşim geçmişi

---

## 🔄 API Rotaları (Endpoints)

### Auth Router (`/auth`)
- `POST /auth/register` - Yeni kullanıcı kaydı
- `POST /auth/login` - Giriş (JWT token döner)
- `GET /auth/profile` - Mevcut kullanıcı profili

### Movies Router (`/movies`)
- `GET /movies/{id}` - Belirli film detayları
- `GET /movies/search` - Film arama

### History Router (`/history`)
- `GET /history` - Kullanıcının izleme geçmişi
- `POST /history` - Yeni geçmiş kaydı

### Recommendation Router (`/recommend`)
- `POST /recommend` - Ruh haliye göre film önerileri (ML modeli kullanır)

### Tags Router (`/tags`)
- `GET /tags` - Etiketleri listele
- `POST /tags` - Yeni etiket oluştur

---

## 🎨 Frontend Rotaları (Pages)

| Rota | Sayfa | Açıklama |
|------|-------|----------|
| `/login` | LoginPage | Kullanıcı girişi |
| `/register` | RegisterPage | Yeni hesap oluştur |
| `/` | MoodSelectionPage | Ruh hali seçim (ana sayfa) |
| `/movies` | RecommendedMoviesPage | Önerilen filmler listesi |
| `/movies/:id` | MovieDetailPage | Seçilen film detayları |
| `/history` | UserHistoryPage | Kullanıcı izleme geçmişi |

---

## 🚀 İş Akışı (User Journey)

1. **Kayıt/Giriş** → LoginPage / RegisterPage
2. **Ruh Hali Seçimi** → MoodSelectionPage (AI'ye ruh hali bilgisini gönder)
3. **Film Önerileri Al** → `/recommend` API çağrısı → RecommendedMoviesPage
4. **Film Detaylarını Gör** → MovieDetailPage
5. **Geçmiş Kontrol** → UserHistoryPage

---

## 🔐 Kimlik Doğrulama Akışı

```
register (email, username, password) 
    ↓
password_hash (bcrypt) → User tablosuna kaydet
    ↓
login (email, password)
    ↓
verify_password + JWT token oluştur
    ↓
Frontend'de token sakla (localStorage/session)
    ↓
Protected endpoints'te token doğrula (get_current_user)
```

---

## 📊 ML Pipeline

```
1. VERİ HAZIRLIK (preprocess.py)
   ├── Film detaylarını işle
   ├── Ruh hali → encoding
   └── Normalization

2. MODEL EĞİTİMİ (automl_train.py)
   ├── AutoML kullanarak en iyi model seç
   └── Modeliyı kaydet (model/ dizinine)

3. TAHMİN (automl_predict.py + recommender.py)
   ├── Kullanıcı ruh hali ve tercihlerini oku
   ├── Önceden eğitilmiş model yükle
   └── En iyi film önerileri döndür
```

---

## 🛠 Geliştirme Ortamı Kuruluşu

### Backend
```bash
# Bağımlılıkları yükle
pip install -r backend/requirements.txt

# Ortam değişkenlerini ayarla (Windows CMD)
setx DB_USER "postgres"
setx DB_PASSWORD "şifren"
setx DB_HOST "localhost"
setx DB_PORT "5432"
setx DB_NAME "film_oneri"

# Sunucuyu başlat
uvicorn backend.app:app --reload
```

### Frontend
```bash
# Bağımlılıkları yükle
npm install

# Geliştirme sunucusunu başlat
npm run dev

# Production build
npm run build
```

---

## 📝 Veri Akışı

```
Frontend (React)
    ↓
API Client (axios/fetch)
    ↓
Backend (FastAPI Routers)
    ↓
Services (Business Logic)
    ↓
Database (PostgreSQL + SQLAlchemy ORM)
    ↓
ML Models (Recommendations)
```

---

## ✅ Proje Özelikleri

- ✅ Kullanıcı kimlik doğrulaması (JWT)
- ✅ Ruh hale dayalı film önerileri
- ✅ İzleme geçmişi takibi
- ✅ Film arama ve filtreleme
- ✅ AutoML tabanlı tahmin modeli
- ✅ Material Design UI
- ✅ Modern React (hooks, Router v7)
- ✅ CORS desteği (frontend-backend iletişim)

