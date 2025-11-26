import React from 'react';
import { Container, TextField, Button, Typography, Box, Paper } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';   // <-- EKLENDİ
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const navigate = useNavigate();

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log('Giriş Yapılıyor...');
  };

  return (
    <Container component="main" maxWidth="xs">
      <Paper 
        elevation={6} 
        sx={{ p: 4, mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}
      >
        
        {/* LOGIN ICON */}
        <PersonIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />

        <Typography component="h1" variant="h5">
          Giriş Yap
        </Typography>

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="E-Posta Adresi"
            name="email"
            autoComplete="email"
            autoFocus
          />

          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Şifre"
            type="password"
            id="password"
            autoComplete="current-password"
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
          >
            Giriş
          </Button>

          <Button 
            fullWidth 
            color="secondary"
            onClick={() => navigate("/register")}
          >
            Hesabınız yok mu? Kayıt Ol
          </Button>

        </Box>
      </Paper>
    </Container>
  );
};

export default LoginPage;
