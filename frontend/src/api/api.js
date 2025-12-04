import axios from "axios";

const API_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

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

// Profile (header ile token gönder)
export const getProfile = async (token) => {
  const response = await api.get("/auth/profile", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

export default api;
