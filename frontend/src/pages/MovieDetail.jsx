import { ArrowBack as BackIcon, FavoriteBorder as LikeBorderIcon, Favorite as LikeIcon, Theaters as WatchIcon } from '@mui/icons-material';
import {
  Alert,
  Box,
  Button,
  Card, CardMedia,
  Chip,
  CircularProgress,
  Container,
  Divider,
  Grid,
  IconButton,
  Paper,
  Snackbar,
  Stack,
  Typography
} from '@mui/material';
import confetti from 'canvas-confetti';
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
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
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

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

  // --- Konfeti Patlatma Fonksiyonu ---
  const triggerConfetti = () => {
    const duration = 3000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

    function randomInRange(min, max) {
      return Math.random() * (max - min) + min;
    }

    const interval = setInterval(function() {
      const timeLeft = animationEnd - Date.now();

      if (timeLeft <= 0) {
        return clearInterval(interval);
      }

      const particleCount = 50 * (timeLeft / duration);
      
      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
      });
      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
      });
    }, 250);
  };

  const handleHistoryAction = async (interactionType) => {
    try {
      setActionLoading(true);
      const response = await addHistoryItem(id, interactionType);
      
      // Backend'den dönen response'a göre state'i güncelle
      if (interactionType === "viewed") {
        // Backend toggle mantığı ile çalışıyor, response'dan is_viewed değerini al
        const previousWatched = isWatched;
        let newWatchedState = false;
        if (response && response.is_viewed !== undefined) {
          newWatchedState = response.is_viewed;
        } else {
          // Fallback: Eğer response'da is_viewed yoksa, action'a göre belirle
          if (response && response.action === "deleted") {
            newWatchedState = false;
          } else if (response && response.action === "created") {
            newWatchedState = true;
          }
        }
        
        setIsWatched(newWatchedState);
        
        // İzleme durumu değiştiğinde alert göster
        if (newWatchedState && !previousWatched) {
          setSnackbar({ open: true, message: '✅ Film izlendi olarak işaretlendi!', severity: 'success' });
        } else if (!newWatchedState && previousWatched) {
          setSnackbar({ open: true, message: 'İzleme geçmişinden kaldırıldı', severity: 'info' });
        }
      } else if (interactionType === "liked") {
        const previousLiked = isLiked;
        // Backend toggle mantığı ile çalışıyor, response'dan is_liked değerini al
        let newLikedState = false;
        if (response && response.is_liked !== undefined) {
          newLikedState = response.is_liked;
        } else {
          // Fallback: Eğer response'da is_liked yoksa, action'a göre belirle
          if (response && response.action === "deleted") {
            newLikedState = false;
          } else if (response && response.action === "created") {
            newLikedState = true;
          }
        }
        
        setIsLiked(newLikedState);
        
        // Beğenilince konfeti patlat ve alert göster
        if (newLikedState && !previousLiked) {
          triggerConfetti();
          setSnackbar({ open: true, message: '❤️ Beğenildi!', severity: 'success' });
        } else if (!newLikedState && previousLiked) {
          setSnackbar({ open: true, message: 'Beğeni geri çekildi', severity: 'info' });
        }
      }
      
    } catch (err) {
      console.error(`${interactionType} işlemi başarısız:`, err);
      setSnackbar({ open: true, message: 'Bir hata oluştu', severity: 'error' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleWatchToggle = () => {
    // Backend toggle mantığı ile çalışıyor, her zaman API isteği gönder
    handleHistoryAction("viewed");
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
              <Stack spacing={2} alignItems="center">
                <Button 
                  variant={isWatched ? "contained" : "outlined"} 
                  startIcon={<WatchIcon />} 
                  fullWidth 
                  onClick={handleWatchToggle}
                  color={isWatched ? "success" : "primary"}
                  disabled={actionLoading}
                  sx={{
                    bgcolor: isWatched ? '#4caf50' : 'transparent',
                    color: isWatched ? 'white' : 'inherit',
                    borderColor: isWatched ? '#4caf50' : 'inherit',
                    '&:hover': {
                      bgcolor: isWatched ? '#388e3c' : 'inherit',
                      transform: 'scale(1.02)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  {actionLoading ? "İşleniyor..." : (isWatched ? "İzlendi ✓" : "İzle")}
                </Button>

                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%' }}>
                  <IconButton
                    onClick={handleLikeToggle}
                    disabled={actionLoading}
                    sx={{
                      color: isLiked ? '#4caf50' : '#757575',
                      backgroundColor: isLiked ? 'rgba(76, 175, 80, 0.1)' : 'transparent',
                      border: isLiked ? '2px solid #4caf50' : '2px solid #e0e0e0',
                      borderRadius: '50%',
                      width: 64,
                      height: 64,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        backgroundColor: isLiked ? 'rgba(76, 175, 80, 0.2)' : 'rgba(0, 0, 0, 0.04)',
                        transform: 'scale(1.15)',
                      },
                      '&:disabled': {
                        opacity: 0.5,
                      }
                    }}
                  >
                    {isLiked ? (
                      <LikeIcon sx={{ fontSize: 36, color: '#4caf50' }} />
                    ) : (
                      <LikeBorderIcon sx={{ fontSize: 36 }} />
                    )}
                  </IconButton>
                </Box>

                <Button 
                  variant="outlined" 
                  fullWidth 
                  onClick={() => navigate('/movies')}
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
      
      {/* Snackbar Alert */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Box
          sx={{
            backgroundColor: snackbar.severity === 'success' ? '#4caf50' : snackbar.severity === 'error' ? '#f44336' : '#2196f3',
            color: 'white',
            padding: '12px 24px',
            borderRadius: '8px',
            fontWeight: 'bold',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          }}
        >
          {snackbar.message}
        </Box>
      </Snackbar>
    </Box>
  );
};

export default MovieDetailPage;