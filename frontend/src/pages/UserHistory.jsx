import React, { useState } from 'react';
import { Container, Typography, Box, Tabs, Tab, Grid } from '@mui/material';
import MovieCard from '../components/MovieCard';
import { mockMovies } from '../data/mockData'; 

// Sahte geçmiş verisi (Gerçekte backend'den çekilecek)
// Basit tutmak için, mockMovies listesini kullanıyoruz
const watchedMovies = mockMovies.slice(0, 2); // İlk 2 film izlenmiş
const likedMovies = [mockMovies[1], mockMovies[2]]; // 2. ve 3. filmler beğenilmiş

// Tab panellerini yönetmek için yardımcı bileşen
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
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const UserHistoryPage = () => {
  const [value, setValue] = useState(0); // 0: İzlenenler, 1: Beğenilenler

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <Container component="main" sx={{ py: 6, minHeight: '100vh' }}>
      <Typography variant="h3" component="h1" gutterBottom color="primary" sx={{ textAlign: 'center', mb: 4 }}>
        Kullanıcı Geçmişi
      </Typography>

      {/* Tabs (Sekmeler) */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs 
            value={value} 
            onChange={handleChange} 
            centered 
            indicatorColor="secondary" 
            textColor="secondary"
        >
          <Tab label={`İzlenenler (${watchedMovies.length})`} />
          <Tab label={`Beğenilenler (${likedMovies.length})`} />
        </Tabs>
      </Box>

      {/* İzlenenler Paneli */}
      <TabPanel value={value} index={0}>
        {watchedMovies.length > 0 ? (
            <Grid container spacing={4}>
                {watchedMovies.map((movie) => (
                    <Grid item key={movie.id} xs={12} sm={6} md={4} lg={3}>
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

      {/* Beğenilenler Paneli */}
      <TabPanel value={value} index={1}>
        {likedMovies.length > 0 ? (
            <Grid container spacing={4}>
                {likedMovies.map((movie) => (
                    <Grid item key={movie.id} xs={12} sm={6} md={4} lg={3}>
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