import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Tabs, Tab, Grid } from '@mui/material';
import MovieCard from '../components/MovieCard';

const TabPanel = (props) => {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const UserHistoryPage = () => {
  const [value, setValue] = useState(0); // Tab seçimi
  const [watchedMovies, setWatchedMovies] = useState([]);
  const [likedMovies, setLikedMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  const handleChange = (event, newValue) => setValue(newValue);

  useEffect(() => {
    const fetchHistory = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;

      try {
        // Backend'deki doğru endpoint
        const res = await fetch("http://localhost:8000/history/me?limit=100&offset=0", {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (!res.ok) throw new Error("Geçmiş yüklenemedi");

        const data = await res.json();

        // Backend interaction tipleri:
        // viewed → izlenen
        // liked → beğenilen
        setWatchedMovies(
          data.items
            .filter(item => item.interaction === "viewed")
            .map(item => item.movie)
        );

        setLikedMovies(
          data.items
            .filter(item => item.interaction === "liked")
            .map(item => item.movie)
        );

      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  return (
    <Container component="main" sx={{ py: 6, minHeight: '100vh' }}>
      <Typography variant="h3" component="h1" gutterBottom color="primary" sx={{ textAlign: 'center', mb: 4 }}>
        Kullanıcı Geçmişi
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={value} onChange={handleChange} centered indicatorColor="secondary" textColor="secondary">
          <Tab label={`İzlenenler (${watchedMovies.length})`} />
          <Tab label={`Beğenilenler (${likedMovies.length})`} />
        </Tabs>
      </Box>

      {/* İZLENENLER */}
      <TabPanel value={value} index={0}>
        {loading ? (
          <Typography align="center">Yükleniyor...</Typography>
        ) : watchedMovies.length > 0 ? (
          <Grid container spacing={4}>
            {watchedMovies.map(movie => (
              <Grid item key={movie.movie_id} xs={12} sm={6} md={4} lg={3}>
                <MovieCard movie={movie} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Typography variant="h6" align="center" color="text.secondary">
            Henüz izlediğiniz bir film yok.
          </Typography>
        )}
      </TabPanel>

      {/* BEĞENİLENLER */}
      <TabPanel value={value} index={1}>
        {loading ? (
          <Typography align="center">Yükleniyor...</Typography>
        ) : likedMovies.length > 0 ? (
          <Grid container spacing={4}>
            {likedMovies.map(movie => (
              <Grid item key={movie.movie_id} xs={12} sm={6} md={4} lg={3}>
                <MovieCard movie={movie} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Typography variant="h6" align="center" color="text.secondary">
            Henüz beğendiğiniz bir film yok.
          </Typography>
        )}
      </TabPanel>
    </Container>
  );
};

export default UserHistoryPage;
