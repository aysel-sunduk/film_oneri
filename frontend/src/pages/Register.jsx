import React from 'react'
import { Container, TextField, Button, Typography, Box, Paper } from '@mui/material'
import PersonAddIcon from '@mui/icons-material/PersonAdd'
import { useNavigate } from 'react-router-dom'  // <-- EKLENDİ

const RegisterPage = () => {

  const navigate = useNavigate(); // <-- YÖNLENDİRME HOOK'U

  const handleSubmit = (event) => {
    event.preventDefault()
    console.log('Kayıt Olunuyor...')
  }

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

          {/* Giriş Sayfasına Yönlendirme */}
          <Button
            fullWidth
            color="secondary"
            onClick={() => navigate("/login")} // <-- BURADA YÖNLENDİRDİK
          >
            Zaten hesabınız var mı? Giriş Yap
          </Button>

        </Box>
      </Paper>
    </Container>
  )
}

export default RegisterPage
