// src/components/MovieCard.jsx

import FavoriteIcon from "@mui/icons-material/Favorite";
import FavoriteBorderIcon from "@mui/icons-material/FavoriteBorder";
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StarIcon from '@mui/icons-material/Star';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardMedia,
  Chip,
  IconButton,
  Rating,
  Snackbar,
  Stack,
  Typography
} from '@mui/material';
import confetti from 'canvas-confetti';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

// Sadece gerekli API fonksiyonlarını import ediyoruz
import {
  addHistoryItem,
  getHistoryByInteraction
} from "../api/api";

const MovieCard = ({ movie }) => {
  const navigate = useNavigate();
  const [alreadyViewed, setAlreadyViewed] = useState(false);
  const [alreadyLiked, setAlreadyLiked] = useState(false);
  const [loading, setLoading] = useState(false); // Global yükleme state'i
  const [historyCheckLoading, setHistoryCheckLoading] = useState(true); // Başlangıç yükleme state'i
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  if (!movie) return null;

  // Token'ı çekmek için localStorage'ı kullanmaya devam ediyoruz
  const token = localStorage.getItem("token"); 

  const {
    movie_id,
    title = "Bilinmeyen Film",
    poster_url,
    rating,
    vote_average,
    genres,
    genre
  } = movie;

  // Genre ve Rating işlemleri
  const parsedGenres = Array.isArray(genres)
    ? genres
    : genre
      ? genre.split(',').map(g => g.trim())
      : [];

  const finalRating = (rating || vote_average || 0);
  const ratingForStars = finalRating / 2;
  const placeholderPoster = "https://placehold.co/400x600?text=No+Image";

  // --- Geçmiş Kontrolü (useEffect) ---
  useEffect(() => {
    const checkHistory = async () => {
      // Token yoksa veya zaten yüklüyorsa işlemi durdur
      if (!token) return;
      setHistoryCheckLoading(true);

      try {
        // 1. İzlenme geçmişini kontrol et
        const viewedRes = await getHistoryByInteraction("viewed");
        setAlreadyViewed(viewedRes.items.some(item => item.movie_id === movie_id));

        // 2. Beğenme geçmişini kontrol et
        const likedRes = await getHistoryByInteraction("liked");
        setAlreadyLiked(likedRes.items.some(item => item.movie_id === movie_id));
        
      } catch (err) {
        console.error("Geçmiş kontrol hatası:", err);
      } finally {
        setHistoryCheckLoading(false);
      }
    };
    checkHistory();
    // movie_id, token değiştiğinde tekrar çalışır
  }, [movie_id, token]);

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

  // --- History Ekleme Fonksiyonu ---
  const sendHistory = async (interactionType) => {
    // API isteği zaten aktifse veya token yoksa işlemi engelle
    if (!token || loading) return; 

    setLoading(true);
    try {
      // user_id'yi göndermeye gerek yok, API fonksiyonu otomatik çekecek
      const response = await addHistoryItem(movie_id, interactionType); 

      // Backend'den dönen response'a göre state'i güncelle
      if (interactionType === "viewed") {
        setAlreadyViewed(true);
      } else if (interactionType === "liked") {
        const previousLiked = alreadyLiked;
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
        
        setAlreadyLiked(newLikedState);
        
        // Beğenilince konfeti patlat ve alert göster
        if (newLikedState && !previousLiked) {
          triggerConfetti();
          setSnackbar({ open: true, message: '❤️ Beğenildi!', severity: 'success' });
        } else if (!newLikedState && previousLiked) {
          setSnackbar({ open: true, message: 'Beğeni geri çekildi', severity: 'info' });
        }
      }

      console.log(`History işlemi: ${interactionType}`, response);
    } catch (err) {
      console.error("History ekleme hatası:", err);
      setSnackbar({ open: true, message: 'Bir hata oluştu', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // --- Buton Etkinlikleri ---
  const handleLike = (e) => {
    e.stopPropagation();
    // Backend toggle mantığı ile çalışıyor, her zaman API isteği gönder
    sendHistory("liked");
  };

  const handleWatch = (e) => {
    e.stopPropagation();
    // Zaten izlenmişse API isteği gönderme
    if (!alreadyViewed) sendHistory("viewed");
  };

  // Kart Tıklama İşlemi
  const handleCardClick = () => {
    navigate(`/movies/${movie_id}`); 
  };
  
  // --- Render ---
  return (
    <Card
      sx={{
        height: '100%',
        borderRadius: 2,
        overflow: 'hidden',
        transition: 'all 0.25s ease',
        cursor: 'pointer',
        '&:hover': {
          transform: 'translateY(-6px)',
          boxShadow: '0 8px 25px rgba(147, 112, 219, 0.35)',
        }
      }}
      onClick={handleCardClick}
    >
      <CardMedia
        component="img"
        height="350"
        image={poster_url || placeholderPoster}
        alt={title}
      />

      <CardContent sx={{ p: 1.5 }} onClick={(e) => e.stopPropagation()}>
        <Typography variant="h6" noWrap>{title}</Typography>

        {/* Puan ve Yıldızlar */}
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
          <Rating
            value={Number(ratingForStars)}
            readOnly
            precision={0.1}
            emptyIcon={<StarIcon style={{ opacity: 0.4 }} fontSize="inherit" />}
            sx={{ fontSize: '1.2rem' }}
          />
          <Typography sx={{ ml: 1, fontWeight: 'bold' }} variant="body2" color="text.secondary">
            {finalRating.toFixed(1)}
          </Typography>
        </Box>

        {/* Türler */}
        {parsedGenres.length > 0 && (
          <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap', minHeight: '30px' }}>
            {parsedGenres.slice(0, 3).map((tag, i) => ( 
              <Chip key={tag + i} label={tag} size="small" variant="outlined" />
            ))}
          </Box>
        )}

        {/* Aksiyon Butonları */}
        <Stack direction="row" spacing={1} sx={{ mt: 2, alignItems: 'center' }}>
          <IconButton
            onClick={handleLike}
            disabled={historyCheckLoading || loading}
            sx={{
              color: alreadyLiked ? '#4caf50' : '#757575',
              backgroundColor: alreadyLiked ? 'rgba(76, 175, 80, 0.1)' : 'transparent',
              border: alreadyLiked ? '2px solid #4caf50' : '2px solid #e0e0e0',
              borderRadius: '50%',
              width: 48,
              height: 48,
              transition: 'all 0.3s ease',
              '&:hover': {
                backgroundColor: alreadyLiked ? 'rgba(76, 175, 80, 0.2)' : 'rgba(0, 0, 0, 0.04)',
                transform: 'scale(1.1)',
              },
              '&:disabled': {
                opacity: 0.5,
              }
            }}
          >
            {alreadyLiked ? (
              <FavoriteIcon sx={{ fontSize: 28, color: '#4caf50' }} />
            ) : (
              <FavoriteBorderIcon sx={{ fontSize: 28 }} />
            )}
          </IconButton>

          <Button
            variant="contained"
            color={alreadyViewed ? "success" : "primary"}
            size="small"
            fullWidth
            startIcon={<PlayArrowIcon />}
            onClick={handleWatch}
            // İzlenmişse, geçmiş kontrolü veya anlık işlem sırasında devre dışı bırak
            disabled={alreadyViewed || historyCheckLoading || loading} 
          >
            {alreadyViewed ? "İzledin" : "İzledim"}
          </Button>
        </Stack>
        
        {/* Yükleme İndikatörü */}
        {(historyCheckLoading || loading) && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block', textAlign: 'center' }}>
                {historyCheckLoading ? "Durum kontrol ediliyor..." : "Kaydediliyor..."}
            </Typography>
        )}
      </CardContent>
      
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
    </Card>
  );
};

export default MovieCard;