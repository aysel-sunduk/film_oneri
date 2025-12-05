// src/pages/Dashboard.jsx
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
        <CircularProgress size={50} />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>

      {/* Başlık Alanı (UI yenilendi) */}
      <Box
        sx={{
          textAlign: 'center',
          mb: 6,
          p: 4,
          borderRadius: 4,
          background: "linear-gradient(135deg, #7b1fa2, #512da8)",
          color: "white",
          boxShadow: "0px 8px 25px rgba(0,0,0,0.25)",
          transition: "0.3s",
          "&:hover": {
            transform: "translateY(-4px)",
          }
        }}
      >
        <Typography variant="h3" fontWeight={700}>
          Hoş Geldin, {userName}!
        </Typography>
        <Typography variant="h6" sx={{ mt: 1, opacity: 0.9 }}>
          Film Önerileri Almaya Hazır mısın?
        </Typography>
      </Box>

      {/* Mood Kartı – İçerik aynı, UI modern */}
      <Paper
        elevation={10}
        sx={{
          p: 4,
          textAlign: 'center',
          borderRadius: 4,
          border: '3px solid',
          borderColor: 'secondary.main',
          boxShadow: "0 10px 25px rgba(0,0,0,0.15)",
          transition: "0.3s",
          "&:hover": {
            transform: "translateY(-8px)",
            boxShadow: "0 15px 35px rgba(0,0,0,0.25)"
          },
        }}
      >
        <MoodIcon color="secondary" sx={{ fontSize: 60, mb: 2 }} />

        <Typography variant="h5" gutterBottom fontWeight={700}>
          Bugün Hangi Ruh Halindesin?
        </Typography>

        <Typography variant="body1" sx={{ mb: 2, opacity: 0.8 }}>
          Sana özel film önerileri almak için mood seç!
        </Typography>

        <Button
          variant="contained"
          color="secondary"
          size="large"
          onClick={() => navigate('/mood')}
          sx={{
            mt: 2,
            py: 1.5,
            px: 5,
            fontWeight: 700,
            borderRadius: 3,
            boxShadow: "0 5px 15px rgba(0,0,0,0.2)",
            "&:hover": {
              boxShadow: "0 8px 25px rgba(0,0,0,0.3)"
            }
          }}
        >
          Mood Seçimine Başla
        </Button>
      </Paper>

    </Container>
  );
};

export default Dashboard;
