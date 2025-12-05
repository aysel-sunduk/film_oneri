import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Tabs, 
  Tab, 
  Grid, 
  CircularProgress,
  Alert,
  Button
} from '@mui/material';
import MovieCard from '../components/MovieCard';
import { getHistoryByInteraction } from '../api/api';

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
  const [value, setValue] = useState(0);
  const [watchedMovies, setWatchedMovies] = useState([]);
  const [likedMovies, setLikedMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  const handleChange = (event, newValue) => setValue(newValue);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log("Token kontrolü:", localStorage.getItem("token"));
      
      // "viewed" etkileşimli filmleri al
      const viewedData = await getHistoryByInteraction("viewed");
      console.log("Viewed API Response:", viewedData);
      
      if (viewedData && viewedData.items) {
        setWatchedMovies(viewedData.items.map(item => item.movie));
      } else {
        setWatchedMovies([]);
      }

      // "liked" etkileşimli filmleri al
      const likedData = await getHistoryByInteraction("liked");
      console.log("Liked API Response:", likedData);
      
      if (likedData && likedData.items) {
        setLikedMovies(likedData.items.map(item => item.movie));
      } else {
        setLikedMovies([]);
      }

    } catch (err) {
      console.error("Geçmiş yüklenirken detaylı hata:", err);
      console.error("Hata response:", err.response);
      console.error("Hata status:", err.response?.status);
      console.error("Hata headers:", err.response?.headers);
      
      let errorMessage = "Geçmiş yüklenemedi";
      
      if (err.response?.status === 401) {
        errorMessage = "Oturum süreniz doldu. Lütfen tekrar giriş yapın.";
        localStorage.removeItem("token");
        setTimeout(() => {
          window.location.href = "/login";
        }, 2000);
      } else if (err.response?.status === 404) {
        errorMessage = "API endpoint'i bulunamadı. Lütfen backend kontrol edin.";
      } else if (err.code === 'ERR_NETWORK') {
        errorMessage = "Bağlantı hatası. Backend çalışıyor mu?";
      } else if (err.message?.includes('CORS')) {
        errorMessage = "CORS hatası. Backend CORS ayarlarını kontrol edin.";
      }
      
      setError(errorMessage + ` (${err.message || ''})`);
      
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [retryCount]);

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

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

      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button color="inherit" size="small" onClick={handleRetry}>
                Tekrar Dene
              </Button>
              <Button color="inherit" size="small" onClick={handleLogout}>
                Çıkış Yap
              </Button>
            </Box>
          }
        >
          {error}
          <br />
          <Typography variant="caption">
            API URL: http://localhost:8000/history/me/
          </Typography>
        </Alert>
      )}

      {/* İZLENENLER */}
      <TabPanel value={value} index={0}>
        {loading ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <CircularProgress />
            <Typography>İzlenen filmler yükleniyor...</Typography>
          </Box>
        ) : watchedMovies.length > 0 ? (
          <Grid container spacing={4}>
            {watchedMovies.map(movie => (
              <Grid item key={movie.movie_id} xs={12} sm={6} md={4} lg={3}>
                <MovieCard movie={movie} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Henüz izlediğiniz bir film yok.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Film izlemeye başladığınızda burada görünecektir.
            </Typography>
          </Box>
        )}
      </TabPanel>

      {/* BEĞENİLENLER */}
      <TabPanel value={value} index={1}>
        {loading ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <CircularProgress />
            <Typography>Beğenilen filmler yükleniyor...</Typography>
          </Box>
        ) : likedMovies.length > 0 ? (
          <Grid container spacing={4}>
            {likedMovies.map(movie => (
              <Grid item key={movie.movie_id} xs={12} sm={6} md={4} lg={3}>
                <MovieCard movie={movie} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Henüz beğendiğiniz bir film yok.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Filmleri beğenmeye başladığınızda burada görünecektir.
            </Typography>
          </Box>
        )}
      </TabPanel>
    </Container>
  );
};

export default UserHistoryPage;