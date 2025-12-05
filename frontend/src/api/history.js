import axios from "./axiosConfig"; // Senin axios ayarın neyse

export const addHistoryItem = async (user_id, movie_id, interaction) => {
  const payload = { user_id, movie_id, interaction };

  const response = await axios.post("/history", payload);
  return response.data;
};
