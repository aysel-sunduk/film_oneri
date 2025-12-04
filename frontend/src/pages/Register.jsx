import React, { useState } from 'react'
import { Container, TextField, Button, Typography, Box, Paper, Snackbar, Alert } from '@mui/material'
import PersonAddIcon from '@mui/icons-material/PersonAdd'
import { useNavigate } from 'react-router-dom'
import api from '../api/api';


const RegisterPage = () => {
  const navigate = useNavigate();

  // Snackbar durumları
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success"); // success, error, warning, info

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') return;
    setOpenSnackbar(false);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const username = event.target.fullName.value;
    const email = event.target.email.value;
    const password = event.target.password.value;

    try {
      const response = await api.post("/auth/register", { username, email, password });
      console.log(response.data);

      setSnackbarMessage("Kayıt başarılı! Giriş sayfasına yönlendiriliyorsunuz.");
      setSnackbarSeverity("success");
      setOpenSnackbar(true);

      // 1-2 saniye sonra login sayfasına yönlendir
      setTimeout(() => {
        navigate("/login");
      }, 1500);

    } catch (error) {
      console.error(error.response?.data?.detail || error.message);

      setSnackbarMessage("Kayıt başarısız: " + (error.response?.data?.detail || ""));
      setSnackbarSeverity("error");
      setOpenSnackbar(true);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Paper elevation={8} sx={{ p: 4, mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <PersonAddIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
        <Typography component="h1" variant="h5">
          Hesap Oluştur
        </Typography>

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="fullName"
            label="Ad Soyad"
            name="fullName"
            autoComplete="name"
            autoFocus
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="E-Posta Adresi"
            name="email"
            autoComplete="email"
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Şifre"
            type="password"
            id="password"
            autoComplete="new-password"
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            sx={{ mt: 3, mb: 2 }}
          >
            Kayıt Ol
          </Button>

          <Button
            fullWidth
            color="secondary"
            onClick={() => navigate("/login")}
          >
            Zaten hesabınız var mı? Giriş Yap
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
  )
}

export default RegisterPage
