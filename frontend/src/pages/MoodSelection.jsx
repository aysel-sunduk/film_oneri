import {
    FlashOn as ExcitementIcon,
    SentimentVerySatisfied as HappyIcon,
    SentimentNeutral as NeutralIcon,
    LocalCafe as RelaxIcon,
    SentimentDissatisfied as SadIcon
} from '@mui/icons-material';
import { Box, Container, Grid, Paper, Typography } from '@mui/material';

// Her ruh halini temsil eden bir obje listesi
const moods = [
  { name: 'Mutlu', icon: HappyIcon, color: 'success' },
  { name: 'Hüzünlü', icon: SadIcon, color: 'info' },
  { name: 'Heyecanlı', icon: ExcitementIcon, color: 'warning' },
  { name: 'Rahat', icon: RelaxIcon, color: 'default' },
  { name: 'Sakin', icon: NeutralIcon, color: 'secondary' },
];

const MoodSelectionPage = () => {
  
  // Mood seçimi yapıldığında çalışacak fonksiyon (şimdilik loglama)
  const handleMoodSelect = (moodName) => {
    console.log(`Seçilen Mood: ${moodName}`);
    // Burada Axios ile bu seçimi backend'e gönderme ve 
    // RecommendedMoviesPage sayfasına yönlendirme işlemi yapılacaktır.
    // navigate('/movies', { state: { mood: moodName } });
  };

  return (
    <Container component="main" sx={{ py: 6, minHeight: '100vh' }}>
      <Box sx={{ textAlign: 'center', mb: 5 }}>
        <Typography variant="h3" component="h1" gutterBottom color="primary">
          Bugün Nasıl Hissediyorsunuz?
        </Typography>
        <Typography variant="h6" color="textSecondary">
          Ruh halinize uygun film önerileri için bir mood seçin.
        </Typography>
      </Box>

      <Grid container spacing={4} justifyContent="center">
        {moods.map((mood) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={mood.name}>
            {/* Mood Butonları: 
              Paper kullanarak butona bir kart görünümü veriyoruz.
              Responsive arayüz için Grid sistemi kullandık.
            */}
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
                  boxShadow: '0 8px 30px rgba(147, 112, 219, 0.5)', // Mor gölge efekti
                },
                backgroundColor: 'background.paper', // Temadaki kart rengini kullan
              }}
              onClick={() => handleMoodSelect(mood.name)}
            >
              {/* İkon */}
              <mood.icon sx={{ fontSize: 80, color: mood.color === 'default' ? 'secondary.main' : `${mood.color}.main`, mb: 1.5 }} />
              
              {/* Mood Adı */}
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