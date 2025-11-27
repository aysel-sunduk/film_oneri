import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import theme from './theme'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

// Sayfa bileşenlerini import edin
import LoginPage from './pages/Login'
import RegisterPage from './pages/Register'
// Diğer sayfaları placeholder olarak ekleyelim:
import MoodSelectionPage from './pages/MoodSelection' 
import RecommendedMoviesPage from './pages/RecommendedMovies'
import MovieDetailPage from './pages/MovieDetail'
import UserHistoryPage from './pages/UserHistory'
import Navbar from './components/Navbar';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline /> 
      <Router>
        <Navbar /> {/* Tüm sayfalarda navbar göster */}
        <Routes>
          {/* Kimlik Doğrulama Rotları */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Ana Uygulama Rotları */}
          <Route path="/" element={<MoodSelectionPage />} /> {/* Varsayılan ana sayfa */}
          <Route path="/movies" element={<RecommendedMoviesPage />} />
          <Route path="/movies/:id" element={<MovieDetailPage />} />
          <Route path="/history" element={<UserHistoryPage />} />

          {/* 404 Sayfası (İsteğe bağlı) */}
          {/* <Route path="*" element={<NotFoundPage />} /> */}
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App