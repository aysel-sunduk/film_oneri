// src/pages/RecommendedMovies.jsx
import React from 'react';
import { Container, Typography, Grid, Box, Alert } from '@mui/material';
import MovieCard from '../components/MovieCard'; // Oluşturduğumuz kartı import edin
import { mockMovies } from '../data/mockData';

const RecommendedMoviesPage = () => {
  // const location = useLocation(); // MoodSelectionPage'den gelen mood verisini almak için kullanılır.
  // const selectedMood = location.state?.mood || "Genel"; // Varsayılan değer

  return (
        <Container component="main" sx={{ py: 6, minHeight: '100vh' }}>
            {/* ... Başlık kısmı ... */}
            <Grid container spacing={4}>
                {/* mockMovies verisini haritalayın */}
                {mockMovies.map((movie) => (
                    <Grid item key={movie.id} xs={12} sm={6} md={4} lg={3}>
                        <MovieCard movie={movie} />
                    </Grid>
                ))}
            </Grid>
        </Container>
    );
};

export default RecommendedMoviesPage;