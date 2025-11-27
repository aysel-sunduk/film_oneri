import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Yönlendirme için
import axios from 'axios'; // API istekleri için
import { 
  Container, Typography, Box, Grid, Paper, CircularProgress, Alert
} from '@mui/material';
import { 
  SentimentVerySatisfied as HappyIcon, 
  SentimentDissatisfied as SadIcon, 
  FlashOn as ExcitementIcon,
  LocalCafe as RelaxIcon,
  SentimentNeutral as NeutralIcon
} from '@mui/icons-material';

// --- API Endpoint ---
const API_URL = 'http://127.0.0.1:5000/predict';

// Her ruh halini temsil eden bir obje listesi
const moods = [
  { name: 'Mutlu', icon: HappyIcon, color: 'success' },
  { name: 'Üzgün', icon: SadIcon, color: 'info' },
  { name: 'Gergin', icon: ExcitementIcon, color: 'warning' },
  { name: 'Romantik', icon: RelaxIcon, color: 'secondary' },
  { name: 'Motive', icon: NeutralIcon, color: 'primary' },
];

const MoodSelectionPage = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleMoodSelect = async (moodName) => {
  try {
    setIsLoading(true);
    const response = await axios.post(API_URL, { overview: moodName });

    const predictedEmotion = response.data.emotion;
    const recommendedMovies = response.data.movies; // backend’den gelen filmler

    console.log('Tahmin Edilen Ruh Hali:', predictedEmotion);
    console.log('Önerilen Filmler:', recommendedMovies);

    // Yönlendirirken filmi de state olarak gönder
    navigate('/movies', { state: { mood: predictedEmotion, movies: recommendedMovies } });

  } catch (err) {
    console.error(err);
    setError('Backend ile bağlantı kurulamadı.');
  } finally {
    setIsLoading(false);
  }
};


  return (
    <Container component="main" sx={{ py: 6, minHeight: '100vh' }}>
      <Box sx={{ textAlign: 'center', mb: 5 }}>
        <Typography variant="h3" component="h1" gutterBottom color="primary">
          🎬 Bugün Nasıl Hissediyorsunuz?
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Ruh halinize uygun film önerileri için bir mood seçin.
        </Typography>
      </Box>

      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress color="primary" size={50} />
          <Typography sx={{ ml: 2, alignSelf: 'center' }}>Öneriler yükleniyor...</Typography>
        </Box>
      )}

      {error && (
        <Box sx={{ my: 4 }}>
          <Alert severity="error">{error}</Alert>
        </Box>
      )}

      <Grid container spacing={4} justifyContent="center">
        {moods.map((mood) => (
          <Grid item xs={12} sm={6} md={4} lg={4} key={mood.name}>
            <Paper 
              elevation={6} 
              sx={{ 
                height: 200, 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center',
                p: 3,
                cursor: 'pointer',
                transition: 'transform 0.3s, box-shadow 0.3s',
                '&:hover': {
                  transform: 'scale(1.05)',
                  boxShadow: '0 8px 30px rgba(147, 112, 219, 0.5)',
                },
                backgroundColor: 'background.paper',
                opacity: isLoading ? 0.6 : 1,
              }}
              onClick={() => !isLoading && handleMoodSelect(mood.name)}
            >
              <mood.icon sx={{ fontSize: 80, color: `${mood.color}.main`, mb: 1.5 }} />
              <Typography variant="h5" component="div" sx={{ fontWeight: 'bold' }}>
                {mood.name}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default MoodSelectionPage;
