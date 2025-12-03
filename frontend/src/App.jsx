import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import theme from './theme'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import MoodSelectionPage from './pages/MoodSelection';
import RecommendedMoviesPage from './pages/RecommendedMovies';
import MovieDetailPage from './pages/MovieDetail';
import UserHistoryPage from './pages/UserHistory';
import LoginPage from './pages/Login';
import RegisterPage from './pages/Register';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navbar />
        <Routes>
          {/* Auth */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Ana Uygulama */}
          <Route path="/" element={<Dashboard />} />
          <Route path="/mood" element={<MoodSelectionPage />} />
          <Route path="/movies" element={<RecommendedMoviesPage />} />
          <Route path="/movies/:id" element={<MovieDetailPage />} />
          <Route path="/history" element={<UserHistoryPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
