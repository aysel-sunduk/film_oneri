import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { getMoviesByEmotions } from "../api/api";
import MovieCard from "../components/MovieCard";
import {
  Container, Grid, Typography,
  CircularProgress, Alert, Box
} from "@mui/material";

export default function RecommendedMovies() {
  const location = useLocation();
  const navigate = useNavigate();

  // MoodSelection'dan gelen ruh halleri listesi
  const { selectedEmotions } = location.state || {}; 
  
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const selectedMoodName = selectedEmotions?.join(", ") || "Seçili Mood Yok";

  useEffect(() => {
    // Eğer state yoksa muhtemelen sayfa yenilendi — kullanıcıyı mood sayfasına yönlendir
    if (!selectedEmotions || selectedEmotions.length === 0) {
      setError("Lütfen film önerisi almak için bir veya daha fazla ruh hali seçin.");
      setLoading(false);
      // küçük gecikme sonra yönlendir
      setTimeout(() => navigate("/mood"), 1200);
      return;
    }

    const fetchRecommendations = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await getMoviesByEmotions(selectedEmotions);
        console.log("By-emotions response:", response);

        const recommendations = response.recommendations || [];
        setMovies(recommendations);

        if (recommendations.length === 0) {
          setError(`"${selectedMoodName}" ruh hali için öneri bulunamadı.`);
        }

      } catch (err) {
        console.error("API Hata:", err);
        setError("Film önerileri yüklenirken bir hata oluştu. Backend servisini kontrol edin.");
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [selectedEmotions, navigate, selectedMoodName]);

  if (loading) {
    return (
      <Container component="main" sx={{ py: 6, minHeight: '100vh', textAlign: 'center' }}>
        <CircularProgress color="primary" />
        <Typography variant="h5" sx={{ mt: 2 }}>"{selectedMoodName}" için öneriler yükleniyor...</Typography>
      </Container>
    );
  }

  return (
    <Container sx={{ mt: 3 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Film Önerileri: {selectedMoodName.toUpperCase()}
      </Typography>

      {error && (
        <Alert severity="warning" sx={{ mb: 3 }}>
            {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {movies.map((movie) => (
          <Grid item xs={12} sm={6} md={4} key={movie.movie_id}>
            <MovieCard movie={movie} />
          </Grid>
        ))}
      </Grid>
      
      {movies.length === 0 && !loading && !error && (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
             <Typography variant="h6" color="text.secondary">
                 Öneri bulunamadı. Lütfen farklı bir ruh hali seçin.
             </Typography>
        </Box>
      )}
    </Container>
  );
}
