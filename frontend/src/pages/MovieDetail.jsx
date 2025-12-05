import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Container, Typography, Box, Grid, Card, CardMedia, Paper, 
  Button, Stack, Divider, CircularProgress, Alert, Chip
} from '@mui/material';
import { Theaters as WatchIcon, Favorite as LikeIcon, ArrowBack as BackIcon } from '@mui/icons-material';
import { addHistoryItem, getHistoryByInteraction } from '../api/api';

const MovieDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [movie, setMovie] = useState(null);
  const [isWatched, setIsWatched] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    const fetchMovieAndHistory = async () => {
      try {
        setLoading(true);
        setError(null);

        // 1. Film detaylarını getir
        const token = localStorage.getItem("token");
        const res = await fetch(`http://localhost:8000/movies/${id}`, {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!res.ok) {
          if (res.status === 404) throw new Error("Film bulunamadı");
          if (res.status === 401) throw new Error("Giriş yapmanız gerekiyor");
          throw new Error(`HTTP hatası: ${res.status}`);
        }

        const data = await res.json();
        setMovie(data);

        // 2. Otomatik olarak "viewed" history ekle (detay sayfası açıldığında)
        try {
          await addHistoryItem(id, "viewed");
          setIsWatched(true);
        } catch (historyErr) {
          console.warn("Viewed history eklenemedi:", historyErr);
        }

        // 3. Kullanıcının bu film için geçmişini kontrol et
        try {
          const viewedHistory = await getHistoryByInteraction("viewed");
          const likedHistory = await getHistoryByInteraction("liked");
          
          const isInViewed = viewedHistory.items?.some(item => item.movie_id === parseInt(id)) || false;
          const isInLiked = likedHistory.items?.some(item => item.movie_id === parseInt(id)) || false;
          
          setIsWatched(isInViewed);
          setIsLiked(isInLiked);
        } catch (historyErr) {
          console.warn("History kontrolü başarısız:", historyErr);
        }

      } catch (err) {
        console.error("Film detayı yükleme hatası:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMovieAndHistory();
  }, [id]);

  const handleHistoryAction = async (interactionType) => {
    try {
      setActionLoading(true);
      await addHistoryItem(id, interactionType);
      
      if (interactionType === "viewed") setIsWatched(true);
      if (interactionType === "liked") setIsLiked(!isLiked); // Toggle işlemi
      
    } catch (err) {
      console.error(`${interactionType} işlemi başarısız:`, err);
      alert(`${interactionType} işlemi başarısız. Lütfen tekrar deneyin.`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleWatchToggle = () => {
    if (!isWatched) {
      handleHistoryAction("viewed");
    }
  };

  const handleLikeToggle = () => {
    handleHistoryAction("liked");
  };

  if (loading) {
    return (
      <Container sx={{ py: 10, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>Film yükleniyor...</Typography>
      </Container>
    );
  }

  if (error || !movie) {
    return (
      <Container sx={{ py: 10, textAlign: 'center' }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error || "Film yüklenirken bir hata oluştu"}
        </Alert>
        <Button 
          variant="contained" 
          onClick={() => navigate('/movies')} 
          startIcon={<BackIcon />}
        >
          Filmlere Geri Dön
        </Button>
      </Container>
    );
  }

  const genres = Array.isArray(movie.genres) 
    ? movie.genres 
    : movie.genre 
    ? movie.genre.split(',').map(g => g.trim())
    : [];

  const backdropUrl = movie.backdrop_url || movie.backdropUrl || "https://placehold.co/1920x1080?text=No+Background";
  const posterUrl = movie.poster_url || movie.posterUrl || "https://placehold.co/400x600?text=No+Poster";
  const rating = movie.vote_average || movie.rating || 0;

  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh' }}>
      <Box
        sx={{
          height: { xs: 250, md: 350 },
          background: `linear-gradient(to top, rgba(28, 22, 37, 1), rgba(28, 22, 37, 0.4)), url(${backdropUrl})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          display: 'flex',
          alignItems: 'flex-end',
          p: { xs: 2, md: 4 }
        }}
      >
        <Typography
          variant="h4"
          component="h1"
          color="white"
          sx={{ 
            fontWeight: 'bold', 
            textShadow: '2px 2px 6px rgba(0,0,0,0.8)',
            maxWidth: '80%'
          }}
        >
          {movie.title} {movie.release_year && `(${movie.release_year})`}
        </Typography>
      </Box>

      <Container sx={{ mt: { xs: -4, md: -6 }, pb: 6 }}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Card sx={{ borderRadius: 2, overflow: 'hidden', boxShadow: 3 }}>
              <CardMedia 
                component="img" 
                image={posterUrl} 
                alt={movie.title} 
                sx={{ 
                  height: { xs: 400, md: 500 }, 
                  width: '100%',
                  objectFit: 'cover' 
                }} 
              />
            </Card>

            <Paper elevation={3} sx={{ p: 2, mt: 3, borderRadius: 2 }}>
              <Stack spacing={1}>
                <Button 
                  variant={isWatched ? "contained" : "outlined"} 
                  startIcon={<WatchIcon />} 
                  fullWidth 
                  onClick={handleWatchToggle}
                  color="primary"
                  disabled={isWatched || actionLoading}
                >
                  {actionLoading ? "İşleniyor..." : (isWatched ? "İzlendi" : "İzle")}
                </Button>

                <Button 
                  variant={isLiked ? "contained" : "outlined"} 
                  startIcon={<LikeIcon />} 
                  fullWidth 
                  onClick={handleLikeToggle}
                  color="secondary"
                  disabled={actionLoading}
                >
                  {actionLoading ? "İşleniyor..." : (isLiked ? "Beğenildi ✓" : "Beğen")}
                </Button>

                <Button 
                  variant="outlined" 
                  fullWidth 
                  onClick={() => navigate('/movies')}
                  sx={{ mt: 1 }}
                >
                  Geri Dön
                </Button>
              </Stack>

              <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                <Typography variant="body2" color="text.secondary">
                  <strong>Puan:</strong> {rating.toFixed(1)}/10
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>Oy Sayısı:</strong> {movie.vote_count || "Bilinmiyor"}
                </Typography>
                {movie.release_date && (
                  <Typography variant="body2" color="text.secondary">
                    <strong>Yayın Tarihi:</strong> {new Date(movie.release_date).toLocaleDateString('tr-TR')}
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={8}>
            <Paper elevation={3} sx={{ p: { xs: 2, md: 4 }, borderRadius: 2, mb: 3 }}>
              <Typography variant="h5" gutterBottom fontWeight="bold">
                Özet
              </Typography>
              <Typography variant="body1" paragraph>
                {movie.overview || movie.summary || "Bu film için özet bulunmuyor."}
              </Typography>
              
              <Divider sx={{ my: 3 }} />
              
              {genres.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    <strong>Türler:</strong>
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {genres.map((genre, index) => (
                      <Chip key={index} label={genre} color="primary" variant="outlined" />
                    ))}
                  </Box>
                </Box>
              )}
              
              {movie.tagline && (
                <Typography variant="body2" color="text.secondary" fontStyle="italic" sx={{ mt: 2 }}>
                  "{movie.tagline}"
                </Typography>
              )}
            </Paper>

            {movie.runtime && (
              <Paper elevation={2} sx={{ p: 2, borderRadius: 2, mb: 2 }}>
                <Typography variant="body2">
                  <strong>Süre:</strong> {movie.runtime} dakika
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default MovieDetailPage;