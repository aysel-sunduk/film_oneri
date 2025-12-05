import {
  Alert, Box,
  CircularProgress,
  Container, Grid, Typography
} from "@mui/material";
import React, { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { getMoviesByEmotions } from "../api/api";
import MovieCard from "../components/MovieCard";

export default function RecommendedMovies() {
  const location = useLocation();
  const navigate = useNavigate();

  // localStorage'dan önceki state'i yükle
  const loadCachedState = () => {
    try {
      const cached = localStorage.getItem('recommendedMoviesState');
      if (cached) {
        const parsed = JSON.parse(cached);
        return {
          selectedEmotions: parsed.selectedEmotions || [],
          movies: parsed.movies || [],
          error: parsed.error || ''
        };
      }
    } catch (err) {
      console.error("localStorage'dan state yüklenirken hata:", err);
    }
    return null;
  };

  // MoodSelection'dan gelen ruh halleri listesi (öncelikli)
  const { selectedEmotions: locationEmotions } = location.state || {}; 
  
  // Cached state'i sadece ilk render'da oku (useRef ile sakla)
  const cachedStateRef = useRef(loadCachedState());
  const cachedState = cachedStateRef.current;
  
  const initialSelectedEmotions = locationEmotions || cachedState?.selectedEmotions || [];
  
  const [movies, setMovies] = useState(cachedState?.movies || []);
  const [loading, setLoading] = useState(!cachedState?.movies); // Eğer cached varsa loading false
  const [error, setError] = useState(cachedState?.error || '');

  const selectedMoodName = initialSelectedEmotions?.join(", ") || "Seçili Mood Yok";

  // State'i localStorage'a kaydet
  const saveStateToCache = (selectedEmotions, movies, error) => {
    try {
      localStorage.setItem('recommendedMoviesState', JSON.stringify({
        selectedEmotions,
        movies,
        error
      }));
    } catch (err) {
      console.error("localStorage'a state kaydedilirken hata:", err);
    }
  };

  useEffect(() => {
    // Eğer location'dan emotions geldiyse (yeni öneri isteği), cached state'i kullanma
    if (locationEmotions && locationEmotions.length > 0) {
      // Yeni öneri isteği - API'den çek
      const fetchRecommendations = async () => {
        setLoading(true);
        setError('');
        try {
          const response = await getMoviesByEmotions(locationEmotions);
          console.log("By-emotions response:", response);

          const recommendations = response.recommendations || [];
          setMovies(recommendations);
          
          // State'i localStorage'a kaydet
          saveStateToCache(locationEmotions, recommendations, '');

          if (recommendations.length === 0) {
            const errorMsg = `"${selectedMoodName}" ruh hali için öneri bulunamadı.`;
            setError(errorMsg);
            saveStateToCache(locationEmotions, [], errorMsg);
          }

        } catch (err) {
          console.error("API Hata:", err);
          const errorMsg = "Film önerileri yüklenirken bir hata oluştu. Backend servisini kontrol edin.";
          setError(errorMsg);
          saveStateToCache(locationEmotions, [], errorMsg);
        } finally {
          setLoading(false);
        }
      };

      fetchRecommendations();
    } else if (cachedState?.movies && cachedState.movies.length > 0) {
      // Cached state var - onu kullan (sayfa geri dönüldüğünde)
      setMovies(cachedState.movies);
      setError(cachedState.error || '');
      setLoading(false);
    } else {
      // Hiçbir state yok - mood sayfasına yönlendir
      setError("Lütfen film önerisi almak için bir veya daha fazla ruh hali seçin.");
      setLoading(false);
      setTimeout(() => navigate("/mood"), 1200);
    }
  }, [locationEmotions, navigate, selectedMoodName]); // cachedState dependency'den çıkarıldı (sadece ilk render'da kullanılacak)

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
