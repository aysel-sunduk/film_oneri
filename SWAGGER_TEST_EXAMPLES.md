# Swagger Test Örnekleri - Film Öneri API

## 🚀 API'yi Başlatma

```cmd
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

## 📖 Swagger UI

Tarayıcıda aç: **http://localhost:8000/docs**

---

## 📝 Endpoint Test Örnekleri

### 1. POST `/recommendation/predict-emotions`
**Açıklama:** Film özetinden duygu tahmini yapar

**Request Body (JSON):**
```json
{
  "overview": "A heartwarming story about a family who goes on an adventure together. Full of laughter, joy, and beautiful moments that will make you smile.",
  "threshold": null
}
```

**Alternatif (Manuel Threshold):**
```json
{
  "overview": "An intense action thriller with explosive scenes and high-speed chases. The hero must save the world from destruction.",
  "threshold": 0.4
}
```

**Beklenen Response:**
```json
{
  "overview": "...",
  "predicted_emotions": ["mutlu", "heyecanlı"],
  "emotion_probabilities": [
    {
      "emotion": "mutlu",
      "probability": 0.85,
      "percentage": "85%"
    },
    {
      "emotion": "heyecanlı",
      "probability": 0.72,
      "percentage": "72%"
    }
  ],
  "probabilities_summary": {
    "mutlu": 0.85,
    "heyecanlı": 0.72,
    "üzgün": 0.15,
    ...
  },
  "top_emotion": "mutlu",
  "threshold": 0.3,
  "confidence_score": 0.85,
  "status": "success",
  "model_type": "autogluon_multi_label"
}
```

---

### 2. POST `/recommendation/by-emotions`
**Açıklama:** Seçilen duygulara göre film önerileri getirir

**Request Body (JSON):**
```json
{
  "selected_emotions": ["mutlu", "romantik"],
  "max_recommendations": 10,
  "min_similarity_threshold": 0.3,
  "emotion_threshold": 0.3
}
```

**Alternatif Örnekler:**

**Sadece Mutlu Filmler:**
```json
{
  "selected_emotions": ["mutlu"],
  "max_recommendations": 5,
  "min_similarity_threshold": 0.4,
  "emotion_threshold": 0.3
}
```

**Heyecanlı ve Motive Edici:**
```json
{
  "selected_emotions": ["heyecanlı", "motive"],
  "max_recommendations": 15,
  "min_similarity_threshold": 0.2,
  "emotion_threshold": 0.25
}
```

**Romantik ve Nostaljik:**
```json
{
  "selected_emotions": ["romantik", "nostaljik"],
  "max_recommendations": 8,
  "min_similarity_threshold": 0.35,
  "emotion_threshold": 0.3
}
```

**Beklenen Response:**
```json
{
  "selected_emotions": ["mutlu", "romantik"],
  "total_recommendations": 10,
  "recommendations": [
    {
      "movie_id": 123,
      "title": "The Movie Title",
      "overview": "A beautiful story about...",
      "similarity_score": 0.85,
      "predicted_emotions": ["mutlu", "romantik", "rahat"],
      "emotion_scores": [
        {
          "emotion": "mutlu",
          "score": 0.92,
          "percentage": "92%"
        },
        {
          "emotion": "romantik",
          "score": 0.88,
          "percentage": "88%"
        }
      ],
      "matched_emotions": ["mutlu", "romantik"],
      "poster_url": "https://example.com/poster.jpg",
      "release_year": 2023,
      "rating": 8.5,
      "genres": ["Comedy", "Romance"],
      "confidence": 0.9
    }
  ],
  "threshold_used": 0.3,
  "min_similarity_threshold": 0.3,
  "status": "success",
  "model_type": "autogluon_multi_label"
}
```

---

### 3. GET `/recommendation/health`
**Açıklama:** Model servisinin durumunu kontrol eder

**Request:** Body gerekmez, sadece "Try it out" butonuna tıkla

**Beklenen Response:**
```json
{
  "status": "ready",
  "model_type": "autogluon_multi_label",
  "loaded_models": 8,
  "target_labels": ["mutlu", "üzgün", "stresli", "motive", "romantik", "heyecanlı", "nostaljik", "rahat"],
  "service_available": true
}
```

---

### 4. GET `/recommendation/emotion-categories`
**Açıklama:** Desteklenen duygu kategorilerini listeler

**Request:** Body gerekmez

**Beklenen Response:**
```json
{
  "emotion_categories": [
    "mutlu",
    "üzgün",
    "stresli",
    "motive",
    "romantik",
    "heyecanlı",
    "nostaljik",
    "rahat"
  ],
  "total_categories": 8
}
```

---

### 5. GET `/recommendation/emotion-distribution`
**Açıklama:** Veritabanındaki filmlerin duygu dağılımını analiz eder

**Request:** Body gerekmez

**Beklenen Response:**
```json
{
  "total_movies_analyzed": 100,
  "total_predictions": 250,
  "emotion_counts": {
    "mutlu": 45,
    "romantik": 38,
    "heyecanlı": 42,
    ...
  },
  "emotion_percentages": {
    "mutlu": 18.0,
    "romantik": 15.2,
    ...
  },
  "most_common_emotion": "mutlu",
  "status": "success"
}
```

---

## 🎯 Swagger'da Test Adımları

1. **API'yi Başlat:**
   ```cmd
   uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Swagger UI'yi Aç:**
   - Tarayıcıda: `http://localhost:8000/docs`

3. **Endpoint'i Seç:**
   - Sol menüden endpoint'i bul (örn: `/recommendation/predict-emotions`)
   - Endpoint'i genişlet (tıkla)

4. **"Try it out" Butonuna Tıkla:**
   - Endpoint'in sağ üst köşesindeki buton

5. **Request Body'yi Doldur:**
   - Yukarıdaki JSON örneklerinden birini kopyala-yapıştır
   - Gerekirse değiştir

6. **"Execute" Butonuna Tıkla:**
   - Sayfanın altındaki yeşil buton

7. **Sonuçları İncele:**
   - Response kısmında sonuçları gör
   - Status code'u kontrol et (200 = başarılı)

---

## ⚠️ Hata Durumları

### Model Hazır Değil (503)
```json
{
  "detail": "Öneri servisi hazır değil. Lütfen önce model eğitildiğinden emin olun."
}
```
**Çözüm:** Önce `python backend/ml/automl_train.py` çalıştır

### Geçersiz Duygu (400)
```json
{
  "detail": "Geçersiz duygu. Mevcut duygular: mutlu, üzgün, ..."
}
```
**Çözüm:** `emotion-categories` endpoint'inden geçerli duyguları kontrol et

### Boş Overview (422)
```json
{
  "detail": [
    {
      "loc": ["body", "overview"],
      "msg": "ensure this value has at least 10 characters"
    }
  ]
}
```
**Çözüm:** Overview en az 10 karakter olmalı

---

## 💡 İpuçları

1. **İlk Test:** Önce `/health` endpoint'ini test et, model hazır mı kontrol et
2. **Duygu Listesi:** `/emotion-categories` ile mevcut duyguları gör
3. **Threshold Değerleri:** 
   - Düşük (0.2-0.3): Daha fazla duygu tahmin eder
   - Yüksek (0.5-0.7): Sadece yüksek güvenilirlikli tahminler
4. **Similarity Threshold:**
   - Düşük (0.2-0.3): Daha fazla film önerir
   - Yüksek (0.5-0.7): Sadece çok uyumlu filmler

---

## 📊 Test Senaryoları

### Senaryo 1: Mutlu Filmler İste
```json
{
  "selected_emotions": ["mutlu"],
  "max_recommendations": 10,
  "min_similarity_threshold": 0.3,
  "emotion_threshold": 0.3
}
```

### Senaryo 2: Çoklu Duygu Kombinasyonu
```json
{
  "selected_emotions": ["romantik", "mutlu", "rahat"],
  "max_recommendations": 15,
  "min_similarity_threshold": 0.25,
  "emotion_threshold": 0.3
}
```

### Senaryo 3: Yüksek Güvenilirlik İste
```json
{
  "selected_emotions": ["heyecanlı"],
  "max_recommendations": 5,
  "min_similarity_threshold": 0.6,
  "emotion_threshold": 0.5
}
```

