# 🎬 Film Öneri Uygulaması — Frontend

Bu klasör React + Vite + Material-UI kullanarak yazılmış frontend uygulamasını içerir.

## 🚀 Kurulum

### 1. Bağımlılıkları Yükle

```bash
npm install
```

### 2. Geliştirme Sunucusunu Başlat

```bash
npm run dev
```

Varsayılan olarak **http://localhost:5173** adresinde çalışır.

### 3. Production Build

```bash
npm run build
```

## 📁 Proje Yapısı

```
src/
├── App.jsx              # Ana uygulama bileşeni (routing)
├── App.css              # Global stiller
├── main.jsx             # React başlangıç noktası
├── theme.js             # Material-UI tema yapılandırması
│
├── api/
│   └── client.js        # API istemcisi (axios/fetch)
│
├── components/
│   ├── Navbar.jsx       # Navigasyon çubuğu
│   └── MovieCard.jsx    # Film kartı bileşeni
│
├── pages/
│   ├── Login.jsx        # Giriş sayfası
│   ├── Register.jsx     # Kayıt sayfası
│   ├── MoodSelection.jsx    # Ruh hali seçimi
│   ├── RecommendedMovies.jsx # Önerilen filmler
│   ├── MovieDetail.jsx  # Film detay sayfası
│   └── UserHistory.jsx  # Kullanıcı geçmişi
│
├── data/
│   └── mockData.js      # Test verisi
│
└── assets/              # Görseller, ikonlar
```

## 🔌 Backend Bağlantısı

Backend API'si şu adreste çalışmalıdır:
```
http://localhost:8000
```

Eğer farklı bir port/host kullanıyorsan, `src/api/client.js` dosyasında `baseURL`'i güncelle.

## 🧪 Örnek API Çağrıları (Frontend'den)

Frontend, backend API'siyle şu şekilde iletişim kurar:

```javascript
// Giriş (Login)
POST /auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

// Film Listesi
GET /movies?page=1&limit=10&genre=Drama

// Film Önerileri
POST /recommendations
{
  "user_id": 1,
  "mood": "happy",
  "genre": "Drama",
  "limit": 10
}
```

## 📦 Dependencies

- **React 19** — UI bileşenleri
- **Vite** — Build tool
- **Material-UI (MUI v7)** — UI komponent kütüphanesi
- **React Router v7** — Sayfa yönlendirmesi
- **Emotion** — CSS-in-JS styling

## 🛠️ ESLint & Formatting

```bash
# Linter çalıştır
npm run lint

# Kodları format et (prettier ile)
npm run format
```

## 🚀 Production Deploy

```bash
# Build ver
npm run build

# Statik dosyaları serv etmek için basit bir HTTP sunucusu başlat
npx http-server dist -p 3000
```

---

**Not:** Backend API'sinin çalıştığından emin ol (http://localhost:8000)!
