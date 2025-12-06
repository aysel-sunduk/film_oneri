import React, { useEffect, useState } from "react";
import { getEmotionCategoriesFromDatabase } from "../api/api";
import { useNavigate } from "react-router-dom";
import {
  Container, Typography, Grid, Button, Paper, Box, Chip,
  CircularProgress, Alert
} from "@mui/material";

export default function MoodSelection() {
  const navigate = useNavigate();
  const [moods, setMoods] = useState([]);
  const [selectedMoods, setSelectedMoods] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    setLoading(true);

    getEmotionCategoriesFromDatabase()
      .then((res) => {
        if (!mounted) return;
        setMoods(res.emotions || []);
      })
      .catch(() => {
        if (!mounted) return;
        setError("Duygu listesi yüklenemedi!");
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => { mounted = false; };
  }, []);

  const handleToggleMood = (mood) => {
    setSelectedMoods((prev) =>
      prev.includes(mood) ? prev.filter((m) => m !== mood) : [...prev, mood]
    );
  };

  const handleGetRecommendations = () => {
    if (selectedMoods.length === 0) {
      alert("Lütfen en az bir ruh hali seçin!");
      return;
    }
    navigate("/movies", { state: { selectedEmotions: selectedMoods } });
  };

  return (
    <Container maxWidth="md" sx={{ pb: 6 }}>
      <Typography
        variant="h3"
        sx={{mt: 20, mb: 2, fontWeight: 800, textAlign: "center" }}
      >
        Nasıl Hissediyorsun?
      </Typography>

      <Typography
        variant="h6"
        sx={{ mb: 4, textAlign: "center", color: "text.secondary" }}
      >
        Bugünkü ruh haline göre film önerelim 🎬
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Box sx={{ textAlign: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <Grid container spacing={3} justifyContent="center">
            {moods.map((mood) => {
              const selected = selectedMoods.includes(mood);
              return (
                <Grid item xs={6} sm={4} md={3} key={mood}>
                  <Paper
                    elevation={selected ? 8 : 2}
                    onClick={() => handleToggleMood(mood)}
                    sx={{
                      p: 3,
                      textAlign: "center",
                      borderRadius: 4,
                      cursor: "pointer",
                      fontWeight: "bold",
                      transition: "0.25s",

                      // 📌 Theme uyumlu renkler
                      background: selected
                        ? "linear-gradient(135deg, #8E24AA, #512DA8)" // purple → deepPurple
                        : "background.paper",
                      color: selected ? "#fff" : "text.primary",

                      border: selected
                        ? "2px solid #AB47BC"
                        : "1px solid #3d2f4d",

                      "&:hover": {
                        transform: "translateY(-4px)",
                        boxShadow: selected ? "0 0 20px #7E57C2" : 6,
                      },
                    }}
                  >
                    {mood}
                  </Paper>
                </Grid>
              );
            })}
          </Grid>

          {/* Selected mood chips */}
          {selectedMoods.length > 0 && (
            <Box
              sx={{
                mt: 4,
                p: 2,
                borderRadius: 3,
                backgroundColor: "rgba(159, 122, 234, 0.12)", // soft purple blur
              }}
            >
              <Typography variant="h6" sx={{ mb: 1 }}>
                Seçilen Ruh Halleri:
              </Typography>

              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                {selectedMoods.map((mood) => (
                  <Chip
                    key={mood}
                    label={mood}
                    onDelete={() => handleToggleMood(mood)}
                    color="secondary"
                    sx={{
                      fontWeight: "bold",
                      borderRadius: "8px",
                    }}
                  />
                ))}
              </Box>
            </Box>
          )}

          {/* Button */}
          <Box sx={{ textAlign: "center", mt: 5 }}>
            <Button
              variant="contained"
              size="large"
              disabled={selectedMoods.length === 0}
              onClick={handleGetRecommendations}
              sx={{
                px: 4,
                py: 1.5,
                borderRadius: 3,
                fontSize: "1.2rem",
                fontWeight: 700,
                background: "linear-gradient(135deg, #7B1FA2, #5E35B1)",
                "&:hover": {
                  boxShadow: "0 0 20px #9575CD",
                },
              }}
            >
              Film Önerisi Al ({selectedMoods.length})
            </Button>
          </Box>
        </>
      )}
    </Container>
  );
}
