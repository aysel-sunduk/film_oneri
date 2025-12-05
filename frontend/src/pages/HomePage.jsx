// src/pages/HomePage.jsx

import React from "react";
import {
  Container,
  Typography,
  Button,
  Box,
  Card,
  CardContent,
  useTheme,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

// Lokal resim import
import homeBg from "../assets/images/home-bg.jpg";

const HomePage = () => {
  const navigate = useNavigate();
  const theme = useTheme();

  return (
    <Box
  sx={{
    minHeight: "100vh",
    display: "flex",
    alignItems: "flex-start", // yukarı hizalama
    justifyContent: "center",
    pt: { xs: 8, sm: 12 }, // üstten boşluk
    position: "relative",
    backgroundImage: `url(${homeBg})`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    backgroundRepeat: "no-repeat",
    "&::before": {
      content: '""',
      position: "absolute",
      top: 0,
      left: 0,
      width: "100%",
      height: "100%",
      backgroundColor: "rgba(28, 22, 37, 0.7)",
      zIndex: 1,
    },
  }}
>
  <Container maxWidth="sm" sx={{ position: "relative", zIndex: 2 }}>
    <Card
      sx={{
        width: "100%",
        textAlign: "center",
        p: { xs: 3, sm: 6 },
        backgroundColor: theme.palette.background.paper,
        borderRadius:
          theme.components.MuiCard.styleOverrides.root.borderRadius,
        boxShadow: theme.shadows[24],
        animation: "fadeIn 1s ease-in-out",
        "@keyframes fadeIn": {
          "0%": { opacity: 0, transform: "translateY(20px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
      }}
    >
      <CardContent>
        <Typography
          variant="h2"
          sx={{
            fontWeight: "extrabold",
            mb: 1,
            color: theme.palette.primary.light,
            letterSpacing: 1.5,
          }}
        >
          🍿 MOVIE MOOD 🎬
        </Typography>

        <Typography
          variant="h5"
          sx={{
            mb: 2,
            color: theme.palette.text.secondary,
            fontWeight: 500,
            fontStyle: "italic",
          }}
        >
          Sana Uygun En İyi Filmi Bul!
        </Typography>

        <Box
          sx={{
            display: "flex",
            flexDirection: { xs: "column", sm: "row" },
            justifyContent: "center",
            gap: 3,
            mt: 4,
          }}
        >
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={() => navigate("/login")}
            sx={{
              flexGrow: 1,
              px: 4,
              py: 1.5,
              fontSize: "1.1rem",
              fontWeight: "bold",
              transition: "transform 0.2s",
              "&:hover": {
                transform: "translateY(-3px)",
                boxShadow: theme.shadows[10],
                backgroundColor: theme.palette.primary.dark,
              },
            }}
          >
            Giriş Yap
          </Button>

          <Button
            variant="outlined"
            color="secondary"
            size="large"
            onClick={() => navigate("/register")}
            sx={{
              flexGrow: 1,
              px: 4,
              py: 1.5,
              fontSize: "1.1rem",
              fontWeight: "bold",
              transition: "transform 0.2s",
              "&:hover": {
                transform: "translateY(-3px)",
                boxShadow: theme.shadows[10],
                borderColor: theme.palette.secondary.dark,
                color: theme.palette.secondary.dark,
                backgroundColor: "rgba(255, 255, 255, 0.05)",
              },
            }}
          >
            Hemen Kayıt Ol
          </Button>
        </Box>
      </CardContent>
    </Card>
  </Container>
</Box>

  );
};

export default HomePage; 