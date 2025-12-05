import axios from "axios";

const API_URL = "http://localhost:8000";

// Axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

// Request interceptor for auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token && !config.url.includes("/recommendation")) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ----------------------------
// 🟦 Recommendation API
// ----------------------------

// Mood listesi – GET
export const getEmotionCategoriesFromDatabase = async () => {
  const response = await api.get("/recommendation/emotions/from-database");
  return response.data;
};

// Mood → Film önerileri – POST
export const getMoviesByEmotions = async (emotions) => {
  const requestBody = {
    selected_emotions: Array.isArray(emotions) ? emotions : [emotions],
    max_recommendations: 10,
    emotion_threshold: 0.3,
    min_similarity_threshold: 0.3,
  };

  const response = await api.post("/recommendation/by-emotions", requestBody);
  return response.data;
};

// Özet → Duygu tahmini – POST
export const predictEmotions = async (overview, threshold = 0.3) => {
  const response = await api.post("/recommendation/predict-emotions", {
    overview,
    threshold,
  });
  return response.data;
};

// ----------------------------
// 🟩 Profile API
// ----------------------------
export const getProfile = async () => {
  const response = await api.get("/auth/profile");
  return response.data;
};

// ----------------------------
// 🟥 History API (Tam Set)
// ----------------------------

// History ekle - Temiz ve Otomatik user_id Çekme Versiyonu
export const addHistoryItem = async (movie_id, interaction) => {
    // 1. Token'ı interceptor zaten ekliyor.

    // 2. FastAPI'deki body.user_id kontrolü için user_id'yi Profile API'den çek
    let userIdToSend = null;
    try {
        const profile = await getProfile();
        if (profile && profile.user_id) {
            userIdToSend = profile.user_id;
        } else {
            throw new Error("Kullanıcı profil bilgileri (user_id) alınamadı.");
        }
    } catch (err) {
        console.error("Profile çekilirken hata oluştu. History kaydı başarısız.", err);
        throw "Oturum bilgileri eksik veya geçersiz. Giriş yapınız.";
    }

    const payload = {
        movie_id,
        interaction,
        user_id: userIdToSend // Otomatik olarak çekilen user_id'yi ekle
    };

    try {
        const response = await api.post("/history", payload);
        return response.data;
    } catch (error) {
        console.error(`[API Error] History ekleme hatası (${interaction}):`, error.response?.data || error.message);
        throw error.response?.data?.detail || "History eklenirken bir hata oluştu.";
    }
};

// Alternatif: user_id gerekmeyen versiyon (backend current_user'dan alır)
export const addHistoryItemSimple = async (movie_id, interaction) => {
  const response = await api.post("/history", {
    movie_id,
    interaction,
    user_id: null // veya hiç eklemeyin
  });
  return response.data;
};

// Kendi history listesi
export const getMyHistory = async () => {
  const response = await api.get("/history/me");
  return response.data;
};

// Interaction'a göre history (viewed, liked, clicked)
export const getHistoryByInteraction = async (interaction) => {
  const response = await api.get(`/history/me/${interaction}`);
  return response.data;
};

// History sil
export const deleteHistoryItem = async (history_id) => {
  const response = await api.delete(`/history/me/${history_id}`);
  return response.data;
};

// Belirli user_id'ye göre history (sadece kendi kullanıcısı için çalışır)
export const getUserHistory = async (user_id) => {
  const response = await api.get(`/history/${user_id}`);
  return response.data;
};

// ----------------------------
// 🟪 Auth API
// ----------------------------
export const login = async (email, password) => {
  const response = await api.post("/auth/login", { email, password });
  return response.data;
};

export const register = async (userData) => {
  const response = await api.post("/auth/register", userData);
  return response.data;
};

// ----------------------------
// 🟨 Movie API
// ----------------------------
export const getMovieDetails = async (movie_id) => {
  const response = await api.get(`/movies/${movie_id}`);
  return response.data;
};

export const searchMovies = async (query) => {
  const response = await api.get("/movies/search", {
    params: { q: query }
  });
  return response.data;
};

export default api;