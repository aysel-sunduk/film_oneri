// src/pages/RecommendedMovies.jsx
import React from 'react';
import { Container, Typography, Grid, Box, Alert } from '@mui/material';
import MovieCard from '../components/MovieCard';
import { useLocation } from 'react-router-dom'; // MoodSelectionPage'den veri almak için

const RecommendedMoviesPage = () => {
  const location = useLocation();
  const movies = location.state?.movies || []; // Backend'den gelen filmler
  const mood = location.state?.mood || "Genel";

  return (
    <Container component="main" sx={{ py: 6, minHeight: '100vh' }}>
      <Box sx={{ textAlign: 'center', mb: 5 }}>
        <Typography variant="h4" gutterBottom>
          {mood} Ruh Haline Uygun Önerilen Filmler
        </Typography>
        {movies.length === 0 && (
          <Alert severity="info">Üzgünüz, bu ruh haline uygun film bulunamadı.</Alert>
        )}
      </Box>

      <Grid container spacing={4}>
        {movies.map((movie, index) => (
          <Grid item key={index} xs={12} sm={6} md={4} lg={3}>
            <MovieCard movie={movie} />
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default RecommendedMoviesPage;
