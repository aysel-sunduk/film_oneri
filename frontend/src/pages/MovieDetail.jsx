import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/api";
import { Box, Typography, CircularProgress, Container, Paper, Chip, useTheme } from "@mui/material"; // useTheme hook'u eklendi
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import StarRateIcon from '@mui/icons-material/StarRate';

// Artık renkler için doğrudan temayı kullanacağız, bu yüzden sabit renk tanımlamalarını kaldırıyoruz.

const MovieDetail = () => {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  
  // Temaya erişim için useTheme hook'u kullanılır
  const theme = useTheme();

  useEffect(() => {
    const fetchMovieDetail = async () => {
      try {
        // Filmin detaylarını API'dan çek
        const res = await api.get(`/movies/${id}`);
        setMovie(res.data);
      } catch (err) {
        console.error("Film detayı alınamadı:", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    fetchMovieDetail();
  }, [id]);

  // Yükleniyor durumu
  if (loading)
    return (
      <Box 
        sx={{ 
          display: "flex", 
          justifyContent: "center", 
          alignItems: "center",
          minHeight: "80vh",
          backgroundColor: theme.palette.background.default, // Temadan arka plan
          color: theme.palette.primary.main, // Temadan primary renk
        }}
      >
        <CircularProgress color="inherit" />
      </Box>
    );

  // Hata veya veri yok durumu
  if (error || !movie)
    return (
      <Box
        sx={{
          backgroundColor: theme.palette.background.default,
          minHeight: "80vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Typography
          variant="h5"
          sx={{ 
            color: theme.palette.error.main, // Temadan hata rengi
            textAlign: "center", 
            padding: "20px",
          }}
        >
          😥 Film detayı yüklenemedi veya bulunamadı.
        </Typography>
      </Box>
    );

  // Başarılı yükleme durumu: Film Detayları
  return (
    <Container 
      maxWidth="lg"
      sx={{ 
        marginTop: "40px", 
        marginBottom: "40px",
        backgroundColor: theme.palette.background.default, // Temadan arka plan
        minHeight: "calc(100vh - 80px)",
        paddingY: "20px",
      }}
    >
      <Paper 
        elevation={15}
        sx={{
          backgroundColor: theme.palette.background.paper, // Temadan kağıt arka plan
          padding: { xs: "25px", sm: "50px" },
          borderRadius: "15px",
          overflow: "hidden",
          borderLeft: `5px solid ${theme.palette.primary.main}`, // Sol kenarda Primary renkli vurgu
        }}
      >
        <Box
          sx={{
            display: "flex",
            flexDirection: { xs: "column", md: "row" },
            color: theme.palette.text.primary, // Temadan ana metin rengi
            gap: "40px",
            alignItems: { xs: "center", md: "flex-start" },
          }}
        >
          {/* Film Posteri */}
          <Box
            sx={{
              width: "280px",
              height: "420px",
              flexShrink: 0,
              position: "relative",
            }}
          >
            <img
              src={
                movie.poster_url ||
                "https://via.placeholder.com/300x450?text=Poster+Yok"
              }
              alt={movie.title}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                borderRadius: "15px",
                // Temanın primary rengini kullanarak gölgeye mor tonu veriyoruz
                boxShadow: `0px 10px 30px rgba(0, 0, 0, 0.8), 0 0 15px ${theme.palette.primary.light}80`, 
              }}
            />
          </Box>

          {/* Film Bilgileri */}
          <Box sx={{ flex: 1, textAlign: { xs: "center", md: "left" } }}>
            <Typography 
              variant="h3" 
              fontWeight="extrabold"
              gutterBottom 
              component="h1"
              sx={{ 
                color: theme.palette.primary.light, // Açık mor tonu
                textShadow: `0 0 5px ${theme.palette.primary.dark}60`, 
              }}
            >
              {movie.title}
            </Typography>
            
            {/* Derecelendirme ve Dil Çipleri */}
            <Box 
              sx={{ 
                display: 'flex', 
                gap: 2, 
                marginBottom: "20px", 
                justifyContent: { xs: "center", md: "flex-start" } 
              }}
            >
              {/* IMDb Puanı */}
              <Chip
                icon={<StarRateIcon />}
                label={`IMDb: ${movie.vote_average ?? "Yok"}`}
                sx={{ 
                  backgroundColor: theme.palette.secondary.main, // Temadan secondary renk
                  color: theme.palette.text.primary, 
                  fontWeight: 'bold' 
                }}
              />
              
              {/* Orjinal Dil */}
              <Chip
                label={`Dil: ${movie.original_language?.toUpperCase() || "-"}`}
                variant="outlined"
                sx={{ 
                  color: theme.palette.text.secondary, // Temadan secondary metin rengi
                  borderColor: theme.palette.text.secondary, 
                }}
              />
            </Box>

            {/* Özet Bölümü */}
            <Typography 
              variant="body1"
              sx={{ 
                marginTop: "15px", 
                lineHeight: 1.7, 
                color: theme.palette.text.primary,
              }}
            >
              <Typography 
                component="span" 
                fontWeight="bold" 
                color={theme.palette.secondary.light} // Özet başlığını temadaki açık secondary ile renklendir
              >
                ÖZET:
              </Typography>{" "}
              {movie.overview || "Film özeti bulunamadı."}
            </Typography>

            <Box sx={{ 
              marginTop: "30px",
              padding: "20px",
              backgroundColor: theme.palette.background.default, // Daha koyu olan default arka planı kullandık
              borderRadius: "10px",
            }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ color: theme.palette.secondary.light }}>
                Detaylı Bilgiler
              </Typography>
              
              {/* Detay Bileşenleri */}
              <DetailItem 
                label="Tür" 
                value={movie.genre || "Belirtilmemiş"} 
                theme={theme}
                              /> 
              <DetailItem label="Çıkış Tarihi" value={movie.release_date || "-"} theme={theme} />
              <DetailItem label="Popülarite" value={movie.popularity?.toFixed(2) || "-"} theme={theme} />
              <DetailItem label="Oy Sayısı" value={movie.vote_count || "-"} theme={theme} />
            </Box>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

// Yeniden kullanılabilir ve temaya bağımlı detay satırı bileşeni
// Temayı doğrudan props olarak DetailItem'a geçirmek yerine, 
// Context API aracılığıyla erişebilmesi için MovieDetail içinde tanımlayabiliriz veya 
// DetailItem'ı da useTheme hook'u ile güncelleyebiliriz. Performans için useTheme hook'u ile güncelliyoruz.
const DetailItem = ({ label, value, icon }) => {
  const theme = useTheme();

  return (
    <Box 
      sx={{ 
        display: "flex", 
        alignItems: "center", 
        marginTop: "10px", 
        borderBottom: `1px dotted ${theme.palette.background.paper}`, // Paper rengini kullanarak hafif ayırıcı
        paddingBottom: '5px',
      }}
    >
      {icon && <Box sx={{ marginRight: 1, color: theme.palette.secondary.main }}>{icon}</Box>}
      <Typography component="span" fontWeight="bold" sx={{ color: theme.palette.text.secondary, minWidth: "120px", display: "inline-block" }}>
          {label}:
      </Typography>
      <Typography component="span" sx={{ color: theme.palette.text.primary, fontWeight: 'medium' }}>
          {value}
      </Typography>
    </Box>
  );
};

export default MovieDetail;