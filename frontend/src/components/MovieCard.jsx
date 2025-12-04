import React from 'react';
import {
  Card,
  CardMedia,
  CardContent,
  Typography,
  Chip,
  Box,
  Rating
} from '@mui/material';
import StarIcon from '@mui/icons-material/Star';
import { Link } from 'react-router-dom';

const MovieCard = ({ movie }) => {
  if (!movie) return null;

  const {
    movie_id,
    title = "Bilinmeyen Film",
    poster_url,
    rating,
    vote_average,
    genres,
    genre,
    predicted_emotions,
    similarity_score
  } = movie;

  // Türler: hem string hem array gelebilir
  const parsedGenres = Array.isArray(genres)
    ? genres
    : genre
    ? genre.split(',').map(g => g.trim())
    : [];

  // Rating hesabı
  const finalRating = ((rating || vote_average) || 0);
  const ratingForStars = finalRating / 2;

  // Poster fallback
  const placeholderPoster = "https://placehold.co/400x600?text=No+Image";

  return (
    <Card
      component={Link}
      to={`/movies/${movie_id}`}
      sx={{
        height: '100%',
        textDecoration: 'none',
        borderRadius: 2,
        overflow: 'hidden',
        transition: 'all 0.25s ease',
        '&:hover': {
          transform: 'translateY(-6px)',
          boxShadow: '0 8px 25px rgba(147, 112, 219, 0.35)',
        }
      }}
    >
      {/* Poster */}
      <CardMedia
        component="img"
        height="350"
        image={poster_url || placeholderPoster}
        alt={title}
        sx={{
          objectFit: 'cover',
          backgroundColor: '#ddd'
        }}
      />

      <CardContent sx={{ p: 1.5 }}>
        {/* Title */}
        <Typography variant="h6" component="h2" noWrap>
          {title}
        </Typography>

        {/* Rating */}
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
          <Rating
            value={Number(ratingForStars)}
            readOnly
            precision={0.1}
            emptyIcon={<StarIcon style={{ opacity: 0.4 }} fontSize="inherit" />}
            sx={{ fontSize: '1.2rem' }}
          />

          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ ml: 1, fontWeight: 'bold' }}
          >
            {finalRating ? finalRating.toFixed(1) : "N/A"}
          </Typography>
        </Box>

        {/* Genres */}
        {parsedGenres.length > 0 && (
          <Box
            sx={{
              mt: 1,
              display: 'flex',
              gap: 0.5,
              flexWrap: 'wrap',
            }}
          >
            {parsedGenres.map((tag, i) => (
              <Chip
                key={tag + i}
                label={tag}
                size="small"
                color="secondary"
                variant="outlined"
              />
            ))}
          </Box>
        )}

        {/* Emotions */}
        {predicted_emotions?.length > 0 && (
          <Box
            sx={{
              mt: 1,
              display: 'flex',
              gap: 0.5,
              flexWrap: 'wrap',
            }}
          >
            {predicted_emotions.slice(0, 3).map((emotion, i) => (
              <Chip
                key={emotion + i}
                label={emotion}
                size="small"
                color="primary"
              />
            ))}
          </Box>
        )}

        {/* Similarity */}
        {similarity_score && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mt: 1, display: 'block' }}
          >
            Benzerlik: {(similarity_score * 100).toFixed(0)}%
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default MovieCard;
