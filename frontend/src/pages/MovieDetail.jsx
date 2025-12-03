import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Typography, Box, Grid, Card, CardMedia, Chip, Button, Rating, Divider, Paper, Stack } from '@mui/material';
import { Theaters as WatchIcon, Favorite as LikeIcon, Star as StarIcon } from '@mui/icons-material';

const MovieDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [movie, setMovie] = useState(null);
  const [isWatched, setIsWatched] = useState(false);
  const [isLiked, setIsLiked] = useState(false);

  // Backend'den film verisini al
  useEffect(() => {
    const fetchMovie = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;

        const res = await fetch(`http://localhost:8000/movies/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (!res.ok) throw new Error("Film yüklenemedi");

        const data = await res.json();
        setMovie(data);

        // Backend history varsa durumu ayarla
        const historyRes = await fetch("http://localhost:8000/history?limit=100&page=1", {
          headers: { Authorization: `Bearer ${token}` }
        });
        const historyData = await historyRes.json();
        const userHistory = historyData.items.find(item => item.movie.movie_id === data.movie_id);
        if (userHistory) {
          setIsWatched(userHistory.interaction === "watched" || userHistory.interaction === "liked");
          setIsLiked(userHistory.interaction === "liked");
        }
      } catch (err) {
        console.error(err);
      }
    };

    fetchMovie();
  }, [id]);

  if (!movie) {
    return (
      <Container sx={{ py: 10, textAlign: 'center' }}>
        <Typography variant="h4" color="error">Film Bulunamadı!</Typography>
        <Button variant="contained" onClick={() => navigate('/movies')} sx={{ mt: 2 }}>Geri Dön</Button>
      </Container>
    );
  }

  // History POST helper
  const postHistory = async (interactionType) => {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      const res = await fetch("http://localhost:8000/history", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          movie_id: movie.movie_id,
          interaction: interactionType
        }),
      });

      if (!res.ok) throw new Error("History kaydedilemedi");

      const data = await res.json();
      console.log("History response:", data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleWatchToggle = async () => {
    const newState = !isWatched;
    setIsWatched(newState);
    if (newState) await postHistory("watched");
  };

  const handleLikeToggle = async () => {
    const newState = !isLiked;
    setIsLiked(newState);
    if (newState) await postHistory("liked");
  };

  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh' }}>
      <Box
        sx={{
          height: { xs: 250, md: 350 },
          background: `linear-gradient(to top, rgba(28, 22, 37, 1), rgba(28, 22, 37, 0.4)), url(${movie.backdropUrl})`,
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
          sx={{ fontWeight: 'bold', textShadow: '2px 2px 6px rgba(0,0,0,0.8)' }}
        >
          {movie.title} ({movie.releaseYear})
        </Typography>
      </Box>

      <Container sx={{ mt: -6, pb: 6 }}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Card sx={{ borderRadius: 2, overflow: 'hidden' }}>
              <CardMedia component="img" image={movie.posterUrl} alt={movie.title} sx={{ height: { xs: 400, md: 500 }, objectFit: 'cover' }} />
            </Card>

            <Paper elevation={3} sx={{ p: 2, mt: 3 }}>
              <Stack spacing={1}>
                <Button variant={isWatched ? "contained" : "outlined"} startIcon={<WatchIcon />} fullWidth onClick={handleWatchToggle} color="primary">
                  {isWatched ? "İzlendi" : "İşaretle"}
                </Button>

                <Button variant={isLiked ? "contained" : "outlined"} startIcon={<LikeIcon />} fullWidth onClick={handleLikeToggle} color="secondary">
                  {isLiked ? "Beğeni Kaldır" : "Beğen"}
                </Button>
              </Stack>
            </Paper>
          </Grid>

          <Grid item xs={12} md={8}>
            <Paper elevation={3} sx={{ p: { xs: 2, md: 4 }, borderRadius: 2 }}>
              {/* Film detayları buraya */}
              <Typography variant="h6" gutterBottom>Özet</Typography>
              <Typography variant="body2" paragraph>{movie.summary}</Typography>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default MovieDetailPage;
