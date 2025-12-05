import React, { useEffect, useState } from 'react';
import {
  Card, CardMedia, CardContent, Typography, Chip, Box, Rating,
  Button, Stack
} from '@mui/material';
import StarIcon from '@mui/icons-material/Star';
import FavoriteIcon from "@mui/icons-material/Favorite";
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { useNavigate } from 'react-router-dom';

import { addHistoryItem, getHistoryByInteraction } from "../api/api";

const MovieCard = ({ movie }) => {
  const navigate = useNavigate();
  const [alreadyViewed, setAlreadyViewed] = useState(false);
  const [alreadyLiked, setAlreadyLiked] = useState(false);

  if (!movie) return null;

  const token = localStorage.getItem("token");

  const {
    movie_id,
    title = "Bilinmeyen Film",
    poster_url,
    rating,
    vote_average,
    genres,
    genre
  } = movie;

  const parsedGenres = Array.isArray(genres)
    ? genres
    : genre
    ? genre.split(',').map(g => g.trim())
    : [];

  const finalRating = ((rating || vote_average) || 0);
  const ratingForStars = finalRating / 2;
  const placeholderPoster = "https://placehold.co/400x600?text=No+Image";

  // Daha önce izlenip izlenmediğini kontrol et
  useEffect(() => {
    const checkHistory = async () => {
      try {
        if (!token) return;
        const viewedRes = await getHistoryByInteraction("viewed", token);
        const likedRes = await getHistoryByInteraction("liked", token);

        setAlreadyViewed(viewedRes.items.some(item => item.movie_id === movie_id));
        setAlreadyLiked(likedRes.items.some(item => item.movie_id === movie_id));
      } catch (err) {
        console.error("Geçmiş kontrol hatası:", err);
      }
    };
    checkHistory();
  }, [movie_id, token]);

  // History ekleme fonksiyonu
  const sendHistory = async (interactionType) => {
    try {
      if (!token) return;

      await addHistoryItem(
        null,
        movie_id,
        interactionType,
        token
      );

      if (interactionType === "viewed") setAlreadyViewed(true);
      if (interactionType === "liked") setAlreadyLiked(true);

      console.log("History eklendi:", interactionType);
    } catch (err) {
      console.error("History ekleme hatası:", err);
    }
  };

  const handleLike = (e) => {
    e.stopPropagation();
    if (!alreadyLiked) sendHistory("liked");
  };

  const handleWatch = (e) => {
    e.stopPropagation();
    if (!alreadyViewed) sendHistory("viewed");
  };

  return (
    <Card
      sx={{
        height: '100%',
        borderRadius: 2,
        overflow: 'hidden',
        transition: 'all 0.25s ease',
        cursor: 'pointer',
        '&:hover': {
          transform: 'translateY(-6px)',
          boxShadow: '0 8px 25px rgba(147, 112, 219, 0.35)',
        }
      }}
      onClick={() => navigate(`/movies/${movie_id}`)} // Tıklanınca detay sayfasına git
    >
      <CardMedia
        component="img"
        height="350"
        image={poster_url || placeholderPoster}
        alt={title}
      />

      <CardContent sx={{ p: 1.5 }} onClick={(e) => e.stopPropagation()}>
        <Typography variant="h6" noWrap>{title}</Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
          <Rating
            value={Number(ratingForStars)}
            readOnly
            precision={0.1}
            emptyIcon={<StarIcon style={{ opacity: 0.4 }} fontSize="inherit" />}
            sx={{ fontSize: '1.2rem' }}
          />
          <Typography sx={{ ml: 1, fontWeight: 'bold' }} variant="body2" color="text.secondary">
            {finalRating.toFixed(1)}
          </Typography>
        </Box>

        {parsedGenres.length > 0 && (
          <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
            {parsedGenres.map((tag, i) => (
              <Chip key={tag + i} label={tag} size="small" variant="outlined" />
            ))}
          </Box>
        )}

        <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
          <Button
            variant="contained"
            color={alreadyLiked ? "success" : "error"}
            size="small"
            fullWidth
            startIcon={<FavoriteIcon />}
            onClick={handleLike}
          >
            {alreadyLiked ? "Beğenildi" : "Beğen"}
          </Button>

          <Button
            variant="contained"
            color={alreadyViewed ? "success" : "primary"}
            size="small"
            fullWidth
            startIcon={<PlayArrowIcon />}
            onClick={handleWatch}
            disabled={alreadyViewed}
          >
            {alreadyViewed ? "Daha önce izledim" : "İzle"}
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default MovieCard;
