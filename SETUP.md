# 🎬 Film Öneri API — Kurulum ve Çalıştırma Rehberi

## 📋 Gereksinimler

- **Python 3.10+**
- **PostgreSQL 12+**
- **pip** (Python paket yöneticisi)

---

## 🚀 Kurulum Adımları

### 1️⃣ PostgreSQL Veritabanı Oluştur

```sql
-- PostgreSQL client'inde çalıştır
CREATE DATABASE film_oneri;
```

### 2️⃣ Ortam Değişkenlerini Ayarla (Windows CMD)

```cmd
setx DB_USER "postgres"
setx DB_PASSWORD "senin_postgres_sifren"
setx DB_HOST "localhost"
setx DB_PORT "5432"
setx DB_NAME "film_oneri"
setx SECRET_KEY "film-oneri-secret-key-12345"
setx ACCESS_TOKEN_EXPIRE_MINUTES "1440"
setx DEBUG "True"
```

**Not:** `setx` komutu sonrası terminali kapatıp yeniden açmalısın!

### 3️⃣ Python Bağımlılıklarını Yükle

```bash
cd d:\Film_oneri\backend
pip install -r requirements.txt
```

### 4️⃣ Veritabanına Film Verilerini İçeri Aktar (Opsiyonel)

```bash
# CSV dosyasından verileri import etmek için (ileride script hazırlayacağız)
# Şimdilik admin panelden veya API üzerinden veri ekleyebilirsin
```

---

## 🎯 API'yi Çalıştır

### Backend Sunucusu Başlat

```bash
cd d:\Film_oneri\backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Çıktı (başarılı başlangıç):**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
```

### Swagger UI Dokümantasyonuna Erişim

Tarayıcında açık: **http://localhost:8000/docs**

---

## 📌 API Endpoint'leri

### 🔐 Kimlik Doğrulama

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/auth/register` | Yeni kullanıcı kaydı |
| POST | `/auth/login` | Giriş (JWT token döner) |
| GET | `/auth/profile` | Mevcut kullanıcı profili |

### 🎥 Filmler

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/movies` | Film listesi (sayfalandırılmış) |
| GET | `/movies/{id}` | Film detayları |
| GET | `/movies/search?q=...` | Film arama |
| POST | `/movies` | Yeni film ekle (admin) |
| PUT | `/movies/{id}` | Film güncelle |
| DELETE | `/movies/{id}` | Film sil |

### 🏷️ Etiketler

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/tags` | Etiketleri listele |
| POST | `/tags` | Yeni etiket ekle |
| DELETE | `/tags/{id}` | Etiket sil |

### 📜 Geçmiş

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/history` | İzleme geçmişi kaydı oluştur |
| GET | `/history` | Kullanıcı geçmişini listele |

### 🤖 Öneriler

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/recommendations` | Kişiselleştirilmiş film önerileri |
| POST | `/recommendations/predict-emotion` | Duygu tahmini |

---

## 🧪 Test Örnekleri (CURL)

### 1. Kullanıcı Kaydı

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "mood": "happy",
    "preferred_genre": "Drama"
  }'
```

### 2. Kullanıcı Girişi

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

**Yanıt (örnek):**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 1
}
```

### 3. Film Listesi (sayfalandırılmış)

```bash
curl -X GET "http://localhost:8000/movies?page=1&limit=10&genre=Drama" \
  -H "Content-Type: application/json"
```

### 4. Film Arama

```bash
curl -X GET "http://localhost:8000/movies/search?q=inception" \
  -H "Content-Type: application/json"
```

### 5. Film Önerileri Al (JWT Token Gerekli)

```bash
curl -X POST "http://localhost:8000/recommendations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "user_id": 1,
    "mood": "happy",
    "genre": "Drama",
    "limit": 10
  }'
```

### 6. İzleme Geçmişi Ekle

```bash
curl -X POST "http://localhost:8000/history" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "user_id": 1,
    "movie_id": 5,
    "interaction": "watched"
  }'
```

---

## 🛠️ Sorun Giderme

### PostgreSQL bağlantısı başarısız

**Hata:** `psycopg2.OperationalError: could not connect to server`

**Çözüm:**
1. PostgreSQL servisinin çalıştığını kontrol et:
```cmd
net start postgresql-x64-15
```
2. Veritabanı adı, kullanıcı adı, şifre doğru mu diye kontrol et

### JWT Token geçersiz

**Hata:** `401 Unauthorized`

**Çözüm:**
1. Login yap ve yeni token al
2. `Authorization: Bearer TOKEN` başlığını kullan

### Veritabanı tabloları oluşturulmadı

**Çözüm:**
1. API'yi çalıştır (startup event otomatik tablo oluşturur)
2. Veya elle SQL sorgusu çalıştır:
```sql
-- backend/db/film_oneri.sql dosyasında bulunur
```

---

## 📦 Proje Yapısı

```
backend/
├── app.py                      # FastAPI ana uygulama
├── config.py                   # Konfigürasyon (ortam değişkenleri)
├── requirements.txt            # Python bağımlılıkları
│
├── core/
│   └── auth.py                 # JWT & şifre yönetimi
│
├── db/
│   ├── connection.py           # PostgreSQL bağlantısı
│   ├── models.py               # SQLAlchemy ORM modelleri
│   └── film_oneri.sql          # SQL şeması
│
├── routers/
│   ├── auth.py                 # Auth endpoint'leri
│   ├── movies.py               # Film endpoint'leri
│   ├── history.py              # Geçmiş endpoint'leri
│   ├── recommendation.py       # Öneri endpoint'leri
│   └── tags.py                 # Etiket endpoint'leri
│
├── schemas/
│   ├── auth.py                 # Auth şemaları (Pydantic)
│   ├── movies.py               # Film şemaları
│   ├── history.py              # Geçmiş şemaları
│   ├── recommendation.py       # Öneri şemaları
│   └── tags.py                 # Etiket şemaları
│
├── services/
│   ├── recommendation_service.py   # Öneri mantığı
│   └── automl_predict.py           # ML model tahminleri
│
└── ml/
    ├── automl_train.py         # Model eğitimi
    ├── preprocess.py           # Veri ön işleme
    └── model/                  # Eğitilmiş modeller

frontend/
├── index.html
├── package.json
├── src/
│   ├── App.jsx
│   ├── pages/
│   ├── components/
│   └── ...
```

---

## 🔥 Sonraki Adımlar

- [ ] Veritabanına 1000+ film verisi yükle (CSV import)
- [ ] AutoML model eğitimi (emotion tahmini)
- [ ] ChatGPT API entegrasyonu (açıklamalı öneriler)
- [ ] Frontend (React) bağlantısı
- [ ] Docker konteynerizasyonu
- [ ] Production deployment (AWS / Azure)

---

## 📞 İletişim & Destek

Herhangi bir soru veya hata raporu için: **github.com/aysel-sunduk/film_oneri**

Happy coding! 🚀
