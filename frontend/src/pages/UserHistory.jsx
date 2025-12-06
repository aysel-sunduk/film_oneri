import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Grid,
  Tab,
  Tabs,
  Typography
} from '@mui/material';
import { useCallback, useEffect, useRef, useState } from 'react';

// API fonksiyonunuz
import { getHistoryByInteraction } from '../api/api';
// MovieCard bileşeniniz
import MovieCard from '../components/MovieCard';


/**
 * Özel TabPanel bileşeni
 */
const TabPanel = (props) => {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const UserHistoryPage = () => {
  // 0: İzlenenler, 1: Beğenilenler
  const [value, setValue] = useState(0); 
  const [watchedMovies, setWatchedMovies] = useState([]);
  const [likedMovies, setLikedMovies] = useState([]);
  const [loading, setLoading] = useState({ viewed: false, liked: false });
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  
  // Verilerin ilk kez çekilip çekilmediğini kontrol etmek için
  const hasFetchedRef = useRef(false);
  const isFetchingRef = useRef(false);

  const handleChange = (event, newValue) => setValue(newValue);

  /**
   * İzlenen ve Beğenilen filmleri API'den çeken ana fonksiyon.
   * @param {boolean} forceRefresh - Önbelleği atlayıp API'den zorla veri çekme.
   */
  const fetchHistory = useCallback(async (forceRefresh = false) => {
    // Aynı anda birden fazla fetch işlemini engelle
    if (isFetchingRef.current && !forceRefresh) {
      console.log("Zaten fetch ediliyor, atlanıyor");
      return;
    }

    // Daha önce fetch edildiyse ve zorla yenileme yapılmıyorsa, atla
    if (hasFetchedRef.current && !forceRefresh) {
      console.log("Veriler zaten fetch edildi, atlanıyor");
      return;
    }

    // Token kontrolü
    if (!localStorage.getItem("token")) {
        setError("Oturumunuzun süresi dolmuş veya giriş yapılmamış. Lütfen giriş yapın.");
        return;
    }

    console.log("fetchHistory çalıştı - forceRefresh:", forceRefresh);
    
    isFetchingRef.current = true;
    setError(null);
    
    // viewed ve liked için istek dizisi
    const requests = [
        { type: "viewed", setter: setWatchedMovies, currentDataLength: watchedMovies.length },
        { type: "liked", setter: setLikedMovies, currentDataLength: likedMovies.length }
    ];

    const results = await Promise.all(requests.map(async (req) => {
        // Sadece zorla yenileme varsa VEYA veri henüz çekilmediyse isteği yap
        if (forceRefresh || req.currentDataLength === 0) {
            setLoading(prev => ({ ...prev, [req.type]: true }));
            try {
                const data = await getHistoryByInteraction(req.type);
                
                if (data && Array.isArray(data.items)) {
                    // HistoryItemResponse'dan Movie objesini çekme
                    req.setter(data.items.map(item => item.movie));
                } else {
                    req.setter([]);
                }
                return { type: req.type, success: true };

            } catch (err) {
                console.error(`${req.type} yüklenirken hata:`, err);
                // API'den gelen detay mesajı varsa onu kullan
                const errorMessage = err.detail || String(err);
                setError(`Geçmiş yüklenemedi: ${errorMessage}`);
                req.setter([]);
                return { type: req.type, success: false };
            } finally {
                setLoading(prev => ({ ...prev, [req.type]: false }));
            }
        }
        return { type: req.type, success: true }; // İstek yapılmadıysa başarılı say
    }));

    // Tüm işlemler tamamlandıktan sonra
    isFetchingRef.current = false;
    hasFetchedRef.current = true;
    
  }, [watchedMovies.length, likedMovies.length]); // Bağımlılıklar: Listelerin uzunlukları ve useCallback için

  /**
   * Bileşen yüklendiğinde ve retryCount değiştiğinde verileri çek.
   */
  useEffect(() => {
    console.log("İlk yükleme için useEffect çalıştı");
    fetchHistory();
    
    // Cleanup function: Bileşen demonte edildiğinde state'i sıfırla
    return () => {
      hasFetchedRef.current = false;
      isFetchingRef.current = false;
    };
  }, [fetchHistory, retryCount]); 

  /**
   * Hata durumunda yeniden deneme
   */
  const handleRetry = () => {
    hasFetchedRef.current = false; // Yeniden çekmeyi zorla
    isFetchingRef.current = false;
    setError(null);
    setWatchedMovies([]);
    setLikedMovies([]);
    setRetryCount(prev => prev + 1); // useEffect'i tetikler
  };

  
  /**
   * MovieCard'dan gelen history değişikliklerini handle eder
   * Beğeni veya izleme durumu değiştiğinde listeyi otomatik günceller
   */
  const handleHistoryChange = useCallback((interactionType, isActive, movieId) => {
    console.log(`History değişti: ${interactionType}, isActive: ${isActive}, movieId: ${movieId}`);
    
    if (interactionType === "liked") {
      if (isActive) {
        // Beğenildi - API'den yeniden çek (yeni eklenen film için)
        getHistoryByInteraction("liked")
          .then(data => {
            if (data && Array.isArray(data.items)) {
              setLikedMovies(data.items.map(item => item.movie));
            }
          })
          .catch(err => console.error("Beğenilenler güncellenirken hata:", err));
      } else {
        // Beğeni geri çekildi - listeden anında çıkar (hızlı geri bildirim için)
        setLikedMovies(prev => prev.filter(m => m.movie_id !== movieId));
      }
    } else if (interactionType === "viewed") {
      if (isActive) {
        // İzlendi - API'den yeniden çek (yeni eklenen film için)
        getHistoryByInteraction("viewed")
          .then(data => {
            if (data && Array.isArray(data.items)) {
              setWatchedMovies(data.items.map(item => item.movie));
            }
          })
          .catch(err => console.error("İzlenenler güncellenirken hata:", err));
      } else {
        // İzleme geri çekildi - listeden anında çıkar (hızlı geri bildirim için)
        setWatchedMovies(prev => prev.filter(m => m.movie_id !== movieId));
      }
    }
  }, []);

  // Tab'e göre yükleme durumu
  const currentTabLoading = value === 0 ? loading.viewed : loading.liked;
  // Tab'e göre film listesi
  const currentMovieList = value === 0 ? watchedMovies : likedMovies;

  return (
    <Container component="main" sx={{ py: 6, minHeight: '100vh' }}>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={value} onChange={handleChange} centered indicatorColor="secondary" textColor="secondary">
          <Tab label={`İzlenenler (${watchedMovies.length})`} />
          <Tab label={`Beğenilenler (${likedMovies.length})`} />
        </Tabs>
      </Box>

      {/* Hata Mesajı */}
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button color="inherit" size="small" onClick={handleRetry} disabled={isFetchingRef.current}>
                Tekrar Dene
              </Button>
            </Box>
          }
        >
          {error}
        </Alert>
      )}

      {/* İÇERİK: İZLENENLER (Index 0) ve BEĞENİLENLER (Index 1) */}
      <TabPanel value={value} index={0}>
        {currentTabLoading ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, pt: 8 }}>
            <CircularProgress />
            <Typography>İzlenen filmler yükleniyor...</Typography>
          </Box>
        ) : currentMovieList.length > 0 ? (
          <Grid container spacing={4}>
            {currentMovieList.map(movie => (
              <Grid item key={movie.movie_id} xs={12} sm={6} md={4} lg={3}>
                {/* MovieCard bileşeni - history değişikliklerini dinlemek için callback ekle */}
                <MovieCard movie={movie} onHistoryChange={handleHistoryChange} /> 
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              {value === 0 ? "Henüz izlediğiniz bir film yok." : "Henüz beğendiğiniz bir film yok."}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {value === 0 ? "Film izlemeye başladığınızda burada görünecektir." : "Filmleri beğenmeye başladığınızda burada görünecektir."}
            </Typography>
          </Box>
        )}
      </TabPanel>

      <TabPanel value={value} index={1}>
        {/* İçerik, yukarıdaki TabPanel ile aynı mantıkla çalışır */}
        {currentTabLoading ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, pt: 8 }}>
            <CircularProgress />
            <Typography>Beğenilen filmler yükleniyor...</Typography>
          </Box>
        ) : currentMovieList.length > 0 ? (
          <Grid container spacing={4}>
            {currentMovieList.map(movie => (
              <Grid item key={movie.movie_id} xs={12} sm={6} md={4} lg={3}>
                <MovieCard movie={movie} onHistoryChange={handleHistoryChange} /> 
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              {value === 0 ? "Henüz izlediğiniz bir film yok." : "Henüz beğendiğiniz bir film yok."}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {value === 0 ? "Film izlemeye başladığınızda burada görünecektir." : "Filmleri beğenmeye başladığınızda burada görünecektir."}
            </Typography>
          </Box>
        )}
      </TabPanel>
    </Container>
  );
};

export default UserHistoryPage;