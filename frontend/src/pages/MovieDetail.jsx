import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Typography, Box, Grid, Card, CardMedia, Chip, Button, Rating, Divider, Paper, Stack } from '@mui/material';
import { Theaters as WatchIcon, Favorite as LikeIcon, Star as StarIcon } from '@mui/icons-material';
import { mockMovies } from '../data/mockData';

const MovieDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const movie = mockMovies.find(m => m.id === parseInt(id));

  const [isWatched, setIsWatched] = useState(false);
  const [isLiked, setIsLiked] = useState(false);

  if (!movie) {
    return (
      <Container sx={{ py: 10, textAlign: 'center' }}>
        <Typography variant="h4" color="error">Film Bulunamadı!</Typography>
        <Button variant="contained" onClick={() => navigate('/movies')} sx={{ mt: 2 }}>
          Geri Dön
        </Button>
      </Container>
    );
  }

  const handleWatchToggle = () => setIsWatched(!isWatched);
  const handleLikeToggle = () => setIsLiked(!isLiked);

  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh' }}>
      
      {/* Backdrop */}
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
          {/* Sol Sütun */}
          <Grid item xs={12} md={4}>
            <Card sx={{ borderRadius: 2, overflow: 'hidden' }}>
              <CardMedia
                component="img"
                image={movie.posterUrl}
                alt={movie.title}
                sx={{ height: { xs: 400, md: 500 }, objectFit: 'cover' }}
              />
            </Card>

            <Paper elevation={3} sx={{ p: 2, mt: 3 }}>
              <Stack spacing={1}>
                <Button
                  variant={isWatched ? "contained" : "outlined"}
                  startIcon={<WatchIcon />}
                  fullWidth
                  onClick={handleWatchToggle}
                  color="primary"
                >
                  {isWatched ? "İzlendi" : "İşaretle"}
                </Button>

                <Button
                  variant={isLiked ? "contained" : "outlined"}
                  startIcon={<LikeIcon />}
                  fullWidth
                  onClick={handleLikeToggle}
                  color="secondary"
                >
                  {isLiked ? "Beğeni Kaldır" : "Beğen"}
                </Button>
              </Stack>
            </Paper>
          </Grid>

          {/* Sağ Sütun */}
          <Grid item xs={12} md={8}>
            <Paper elevation={3} sx={{ p: { xs: 2, md: 4 }, borderRadius: 2 }}>
              
              {/* Rating ve Genre */}
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 1 }}>
                <Rating
                  value={movie.rating / 2}
                  readOnly
                  precision={0.1}
                  size="large"
                  emptyIcon={<StarIcon style={{ opacity: 0.55 }} fontSize="inherit" />}
                />
                <Typography variant="h6" sx={{ ml: 1, fontWeight: 'bold', color: 'primary.light' }}>
                  {movie.rating} / 10
                </Typography>
                <Divider orientation="vertical" flexItem sx={{ mx: 2 }} />
                {movie.genre.map(tag => (
                  <Chip key={tag} label={tag} color="secondary" size="small" />
                ))}
              </Box>

              <Divider sx={{ mb: 2 }} />

              {/* Özet */}
              <Typography variant="h6" gutterBottom>Özet</Typography>
              <Typography variant="body2" paragraph>{movie.summary}</Typography>

              <Divider sx={{ my: 2 }} />

              {/* Yönetmen ve Yıl */}
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle1" color="primary">Yönetmen</Typography>
                  <Typography variant="body2">{movie.director}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle1" color="primary">Çıkış Yılı</Typography>
                  <Typography variant="body2">{movie.releaseYear}</Typography>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              {/* Oyuncular */}
              <Typography variant="subtitle1" color="primary" gutterBottom>Başlıca Oyuncular</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {movie.cast.map(actor => (
                  <Chip key={actor} label={actor} variant="outlined" size="small" />
                ))}
              </Box>

            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default MovieDetailPage;
