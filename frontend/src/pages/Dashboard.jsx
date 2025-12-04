// src/pages/Dashboard.jsx - Güncellenmiş hali
import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, Button, Paper, CircularProgress } from '@mui/material';
import MoodIcon from '@mui/icons-material/Mood';
import { useNavigate } from 'react-router-dom';
import { getProfile } from "../api/api";


const Dashboard = () => {
  const navigate = useNavigate();
  const [userName, setUserName] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuthAndGetProfile = async () => {
      const token = localStorage.getItem('token');

      if (!token) {
        navigate('/login');
        return;
      }

      try {
        // Profil bilgilerini getir
        const profile = await getProfile(token);

        setUserName(profile.username || 'Movie Lover');
      } catch (error) {
        console.error('Profil yüklenemedi:', error);
        setUserName('Movie Lover');
      } finally {
        setLoading(false);
      }
    };

    checkAuthAndGetProfile();
  }, [navigate]);

  if (loading) {
    return (
      <Container sx={{ py: 10, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ 
        textAlign: 'center', 
        mb: 6, 
        p: 3, 
        bgcolor: 'primary.light', 
        borderRadius: 2,
        color: 'primary.contrastText' 
      }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          Hoş Geldin, {userName}!
        </Typography>
        <Typography variant="h6">
          Film Önerileri Almaya Hazır mısın?
        </Typography>
      </Box>

      <Paper 
        elevation={10} 
        sx={{ 
          p: 4, 
          mb: 6, 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          border: '3px solid',
          borderColor: 'secondary.main',
          transition: 'transform 0.3s',
          '&:hover': {
            transform: 'translateY(-5px)',
            boxShadow: 15
          }
        }}
      >
        <MoodIcon color="secondary" sx={{ fontSize: 60, mb: 2 }} />
        <Typography variant="h5" gutterBottom>
          Bugün Hangi Ruh Halindesin?
        </Typography>
        <Button
          variant="contained"
          color="secondary"
          size="large"
          onClick={() => navigate('/mood')}
          sx={{ mt: 2, py: 1.5, px: 5, fontWeight: 700 }}
        >
          Mood Seçimine Başla
        </Button>
      </Paper>
    </Container>
  );
};

export default Dashboard;