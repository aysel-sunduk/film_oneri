import React, { useEffect, useState } from "react";
import { getEmotionCategoriesFromDatabase } from "../api/api";
import { useNavigate } from "react-router-dom";
import { Container, Typography, Grid, Button, Paper, Box, Chip, CircularProgress, Alert } from "@mui/material";

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
    setSelectedMoods(prev => {
      if (prev.includes(mood)) {
        return prev.filter(m => m !== mood);
      } else {
        return [...prev, mood];
      }
    });
  };

  const handleGetRecommendations = () => {
    if (selectedMoods.length === 0) {
      alert("Lütfen en az bir ruh hali seçin!");
      return;
    }
    // Seçimleri state olarak gönder
    navigate("/movies", { state: { selectedEmotions: selectedMoods } });
  };

  return (
    <Container>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Nasıl bir ruh halindesin?
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {loading ? (
        <Box sx={{ textAlign: 'center', py: 6 }}><CircularProgress /></Box>
      ) : (
        <>
          <Typography variant="body1" sx={{ mb: 2, color: 'text.secondary' }}>
            Bir veya daha fazla ruh hali seçebilirsiniz:
          </Typography>

          <Grid container spacing={2} sx={{ mb: 3 }}>
            {moods.map((mood) => {
              const isSelected = selectedMoods.includes(mood);
              return (
                <Grid item xs={6} sm={4} md={3} key={mood}>
                  <Paper
                    onClick={() => handleToggleMood(mood)}
                    sx={{
                      p: 2,
                      textAlign: "center",
                      cursor: "pointer",
                      fontWeight: "bold",
                      backgroundColor: isSelected ? "primary.main" : "background.paper",
                      color: isSelected ? "primary.contrastText" : "text.primary",
                      border: isSelected ? "2px solid" : "1px solid",
                      borderColor: isSelected ? "primary.main" : "divider",
                      transition: "all 0.2s ease-in-out",
                      "&:hover": {
                        backgroundColor: isSelected ? "primary.dark" : "action.hover",
                        transform: "translateY(-2px)",
                        boxShadow: 2
                      }
                    }}
                  >
                    {mood}
                  </Paper>
                </Grid>
              );
            })}
          </Grid>

          {selectedMoods.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Seçilen Ruh Halleri:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {selectedMoods.map((mood) => (
                  <Chip
                    key={mood}
                    label={mood}
                    onDelete={() => handleToggleMood(mood)}
                    color="primary"
                    variant="filled"
                  />
                ))}
              </Box>
            </Box>
          )}

          <Box sx={{ textAlign: 'center', mt: 3 }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={handleGetRecommendations}
              disabled={selectedMoods.length === 0}
              sx={{
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 'bold'
              }}
            >
              Film Önerileri Al ({selectedMoods.length} ruh hali seçildi)
            </Button>
          </Box>
        </>
      )}
    </Container>
  );
}