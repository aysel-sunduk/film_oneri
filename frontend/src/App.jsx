import { ThemeProvider } from "@mui/material/styles";
import { CssBaseline } from "@mui/material";
import theme from "./theme";   

import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import Navbar from "./components/Navbar";

// Pages
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/Login";
import RegisterPage from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Mood from "./pages/MoodSelection";
import Movies from "./pages/RecommendedMovies";
import History from "./pages/UserHistory";
import MovieDetail from "./pages/MovieDetail";

function AppContent() {
  const location = useLocation();
  const hideNavbarPaths = ["/", "/login", "/register"];
  const hideNavbar = hideNavbarPaths.includes(location.pathname);

  return (
    <>
      {!hideNavbar && <Navbar />}

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/mood" element={<Mood />} />
        <Route path="/movies" element={<Movies />} />
        <Route path="/history" element={<History />} />
        <Route path="/movies/:id" element={<MovieDetail />} />

      </Routes>
    </>
  );
}

export default function App() {
  return (
    <ThemeProvider theme={theme}>    
      <CssBaseline />                
      <Router>
        <AppContent />
      </Router>
    </ThemeProvider>
  );
}
