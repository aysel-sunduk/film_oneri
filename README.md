# 🎬 Film Öneri Uygulaması

Kullanıcıların duygu durumuna, tercihlerine ve izleme geçmişine göre kişiselleştirilmiş film önerileri sunan **full-stack web uygulaması**.

## ✨ Temel Özellikler

✅ **Kullanıcı Yönetimi**
- Kayıt (signup) ve giriş (login)
- JWT token tabanlı güvenlik
- Profil yönetimi

✅ **Film Veritabanı**
- 1000+ film (IMDB veri seti)
- Gelişmiş arama ve filtreleme
- Film detayları (yönetmen, oyuncular, puanlar vb.)

✅ **Akıllı Öneri Sistemi**
- 🎯 **İçerik Tabanlı Filtreleme** — Tür, puanı, yönetmen benzerlikleri
- 🤖 **Duygu Tabanlı Öneriler** — Kullanıcının seçtiği mood'a uygun filmler
- 🧠 **ML Tahminleri** — AutoML ile film açıklamasından duygu analizi

✅ **Kullanıcı Geçmişi**
- İzlenen filmler
- Beğenilen filmler
- Etkileşim takibi (geliştirilmiş öneriler için)

✅ **Modern Teknoloji Stack**
- **Backend:** FastAPI (Python)
- **Frontend:** React 19 + Vite + Material-UI
- **Veritabanı:** PostgreSQL
- **Auth:** JWT + bcrypt
- **Styling:** Emotion (CSS-in-JS)

---

## 📁 Proje Yapısı

```
Film_oneri/
│
├── backend/                    # FastAPI uygulaması
│   ├── app.py                 # Ana uygulama
│   ├── config.py              # Konfigürasyon
│   ├── requirements.txt        # Python bağımlılıkları
│   │
│   ├── core/
│   │   └── auth.py            # JWT & şifre yönetimi
│   │
│   ├── db/
│   │   ├── connection.py       # PostgreSQL bağlantısı
│   │   ├── models.py           # SQLAlchemy ORM
│   │   └── film_oneri.sql      # SQL şeması
│   │
│   ├── routers/
│   │   ├── auth.py            # Kimlik doğrulama
│   │   ├── movies.py          # Film yönetimi
│   │   ├── history.py         # İzleme geçmişi
│   │   ├── recommendation.py  # Öneriler
│   │   └── tags.py            # Etiketleme
│   │
│   ├── schemas/
│   │   └── *.py               # Pydantic şemaları
│   │
│   ├── services/
│   │   ├── recommendation_service.py
│   │   └── automl_predict.py
│   │
│   └── ml/
│       ├── automl_train.py
│       ├── preprocess.py
│       └── model/
│
├── frontend/                   # React uygulaması
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── pages/
│       ├── components/
│       ├── api/
│       └── theme.js
│
├── SETUP.md                   # Kurulum rehberi
├── PROJECT_SKELETON.md        # Proje mimarisi dokumentasyonu
└── run_api.bat               # Windows başlangıç script'i
```

---

## 🚀 Hızlı Başlangıç

### 📦 Gereksinimler

- Python 3.10+
- Node.js 16+
- PostgreSQL 12+

### 1️⃣ Backend Kurulumu

```bash
# Ortam değişkenlerini ayarla (Windows CMD)
setx DB_USER "postgres"
setx DB_PASSWORD "senin_sifren"
setx DB_HOST "localhost"
setx DB_PORT "5432"
setx DB_NAME "film_oneri"

# Terminali yeniden açtıktan sonra:
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

**API şu adresle çalışacak:** http://localhost:8000

### 2️⃣ Frontend Kurulumu

```bash
cd frontend
npm install
npm run dev
```

**Frontend şu adresle açılacak:** http://localhost:5173

---

## 📚 API Dokümantasyonu

### 🔐 Kimlik Doğrulama

```bash
# Kayıt
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "securepass123",
    "mood": "happy"
  }'

# Giriş
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

### 🎥 Filmler

```bash
# Listeyi getir
curl http://localhost:8000/movies?page=1&limit=10&genre=Drama

# Ara
curl http://localhost:8000/movies/search?q=inception
```

### 🤖 Öneriler

```bash
curl -X POST http://localhost:8000/recommendations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "mood": "happy",
    "genre": "Drama",
    "limit": 10
  }'
```

### 📖 Swagger UI

Tüm endpoint'leri interaktif olarak test et:
```
http://localhost:8000/docs
```

---

## 🛠️ Geliştirme

### Backend Testleri Çalıştır

```bash
cd backend
pytest -v
```

### Kod Formatlama (Black)

```bash
black backend/
```

### Lint Kontrol (Flake8)

```bash
flake8 backend/
```

---

## 📊 Veritabanı Şeması

### Ana Tablolar

| Tablo | Açıklama |
|-------|----------|
| `users` | Kullanıcı hesapları |
| `movies` | Film verileri |
| `emotions` | Film duygusal etiketleri |
| `user_history` | İzleme geçmişi |
| `movie_tags` | Film etiketleri |

### Örnek Sorgu

```sql
-- Kullanıcının happy filmlerini öner
SELECT m.* FROM movies m
JOIN emotions e ON m.movie_id = e.movie_id
WHERE e.emotion_label LIKE '%happy%'
  AND m.movie_id NOT IN (
    SELECT movie_id FROM user_history 
    WHERE user_id = 1
  )
ORDER BY m.imdb_rating DESC
LIMIT 10;
```

---

## 🚢 Deployment

### Docker (Opsiyonel)

```bash
# Backend Dockerfile
docker build -t film-oneri-api ./backend
docker run -p 8000:8000 film-oneri-api

# Frontend Dockerfile
docker build -t film-oneri-web ./frontend
docker run -p 3000:3000 film-oneri-web
```

### Production Checklist

- [ ] SECRET_KEY'i güvenli bir değerle değiştir
- [ ] CORS origins'i kısıtla
- [ ] PostgreSQL backup'ı yapılandır
- [ ] SSL sertifikası ekle
- [ ] Rate limiting implement et
- [ ] Logging'i ayarla
- [ ] Monitoring (Sentry, DataDog) entegrasyonu

---

## 📝 Örnek Workflow

1. **Kullanıcı kaydolur** → JWT token alır
2. **Ruh halini seçer** (örn: "happy")
3. **Backend öneriler getir** (`GET /recommendations`)
4. **Film detayını görüntüle** (`GET /movies/{id}`)
5. **İzledim işaretle** (`POST /history`)
6. **Sistem kaydeder** ve sonraki öneriler iyileştirilir

---

## 🐛 Bilinen Sorunlar

- [ ] ML modeli henüz training verileri ile test edilmedi
- [ ] ChatGPT API entegrasyonu pending
- [ ] Frontend sayfa geçişlerinde loading state eklenecek

---

## 🔄 Gelecek Özellikler

- [ ] Sosyal paylaşım (yorum, beğeni)
- [ ] Kolaboratif filtreleme (user-user öneriler)
- [ ] Mobil uygulama (React Native)
- [ ] Real-time notifications (WebSocket)
- [ ] Admin dashboard
- [ ] Analytics & insights

---

## 📞 İletişim

**Geliştirici:** Aysel Sunduk  
**GitHub:** [aysel-sunduk/film_oneri](https://github.com/aysel-sunduk/film_oneri)  
**Sorunlar:** GitHub Issues'de bildir

---

## 📄 Lisans

MIT License — Özgürce kullan ve modifike et

---

**Proje Durumu:** 🔄 Aktif Geliştirme  
**Son Güncelleme:** Kasım 2025  
**Version:** 1.0.0
