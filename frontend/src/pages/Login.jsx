import React, { useState } from 'react';
import { Container, TextField, Button, Typography, Box, Paper, Snackbar, Alert } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/api';

const LoginPage = () => {
  const navigate = useNavigate();

  // Snackbar durumları
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') return;
    setOpenSnackbar(false);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const email = event.target.email.value;
    const password = event.target.password.value;

    try {
      const response = await api.post("/auth/login", { email, password });
      console.log(response.data);


      // Başarılı giriş mesajı
      setSnackbarMessage("Giriş başarılı! Anasayfaya yönlendiriliyorsunuz.");
      setSnackbarSeverity("success");
      setOpenSnackbar(true);

      localStorage.setItem("token", response.data.token);
      window.dispatchEvent(new Event("loginStatusChanged"));

      navigate("/");

    } catch (error) {
      console.error(error.response?.data?.detail || error.message);

      setSnackbarMessage("Giriş başarısız: " + (error.response?.data?.detail || ""));
      setSnackbarSeverity("error");
      setOpenSnackbar(true);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Paper 
        elevation={6} 
        sx={{ p: 4, mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}
      >
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

      {/* Snackbar */}
      <Snackbar
        open={openSnackbar}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default LoginPage;
