// src/components/MovieCard.jsx
import React from 'react';
import { Card, CardMedia, CardContent, Typography, Chip, Box, Rating } from '@mui/material';
import StarIcon from '@mui/icons-material/Star';
import { Link } from 'react-router-dom';

const MovieCard = ({ movie }) => {
  return (
    // Link bileşenini kullanarak kartın Film Detay sayfasına gitmesini sağlıyoruz
    <Card 
      component={Link}
      to={`/movies/${movie.id}`} // Dinamik rota
      sx={{ 
        height: '100%', 
        textDecoration: 'none', 
        transition: 'transform 0.3s',
        '&:hover': {
          transform: 'scale(1.05)',
          boxShadow: '0 5px 25px rgba(147, 112, 219, 0.7)', // Mor tema vurgusu
        }
      }}
    >
      {/* Film Posteri */}
      <CardMedia
        component="img"
        height="350"
        image={movie.posterUrl}
        alt={movie.title}
        sx={{ objectFit: 'cover' }}
      />
      
      <CardContent sx={{ pb: 1, pt: 1 }}>
        {/* Başlık */}
        <Typography gutterBottom variant="h6" component="div" noWrap>
          {movie.title}
        </Typography>

        {/* Rating ve Etiketler */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          
          {/* Rating */}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Rating
              value={movie.rating / 2} // 10 üzerinden puanı 5'lik yıldıza çevir
              readOnly
              precision={0.1}
              emptyIcon={<StarIcon style={{ opacity: 0.55 }} fontSize="inherit" />}
            />
            <Typography variant="body2" color="text.secondary" sx={{ ml: 1, fontWeight: 'bold' }}>
              {movie.rating}
            </Typography>
          </Box>
        </Box>

        {/* Genre Etiketleri */}
        <Box sx={{ mt: 1, display: 'flex', gap: 0.5, overflowX: 'auto' }}>
            {movie.genre.map((tag) => (
                <Chip key={tag} label={tag} size="small" color="secondary" />
            ))}
        </Box>
      </CardContent>
    </Card>
  );
};

// Bu bileşeni src/components/MovieCard.jsx olarak kaydedin.
export default MovieCard;