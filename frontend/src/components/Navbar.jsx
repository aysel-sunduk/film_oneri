import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, IconButton, Menu, MenuItem } from '@mui/material';
import MovieIcon from '@mui/icons-material/Movie';
import MenuIcon from '@mui/icons-material/Menu';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();

  // Login durumu
  const [isLoggedIn, setIsLoggedIn] = useState(() => !!localStorage.getItem("token"));

  useEffect(() => {
    const checkLogin = () => setIsLoggedIn(!!localStorage.getItem("token"));
    window.addEventListener("storage", checkLogin);
    window.addEventListener("loginStatusChanged", checkLogin);
    return () => {
      window.removeEventListener("storage", checkLogin);
      window.removeEventListener("loginStatusChanged", checkLogin);
    };
  }, []);

  // Mobil menü
  const [anchorElNav, setAnchorElNav] = useState(null);
  const handleOpenNavMenu = (event) => setAnchorElNav(event.currentTarget);
  const handleCloseNavMenu = () => setAnchorElNav(null);

  // Logout
  const handleLogout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");

  window.dispatchEvent(new Event("loginStatusChanged"));

  setIsLoggedIn(false);
  navigate("/login");
};


  // Menü seçenekleri (sadece girişli kullanıcı için)
  const navItems = [
    { label: 'Mood Seçimi', path: '/mood' },
    { label: 'Önerilenler', path: '/movies' },
    { label: 'Geçmişim', path: '/history' },
  ];

  return (
    <AppBar position="sticky" sx={{ bgcolor: 'background.paper', boxShadow: 3 }}>
      <Toolbar sx={{ justifyContent: 'space-between', minHeight: { xs: 64, md: 70 } }}>

        {/* Sol Logo */}
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: { xs: 1, md: 0 } }}>
          {/* Masaüstü */}
          <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', mr: 3 }}>
            <MovieIcon sx={{ fontSize: 32, color: 'primary.main', mr: 1.5 }} />
            <Typography
              variant="h5"
              component={Link}
              to="/"  // Dashboard'a yönlendir
              sx={{
                fontWeight: 700,
                color: 'text.primary',
                textDecoration: 'none',
                '&:hover': { color: 'primary.main' }
              }}
            >
              MOVIE MOOD
            </Typography>
          </Box>

          {/* Mobil */}
          <Box sx={{ display: { xs: 'flex', md: 'none' }, alignItems: 'center', flexGrow: 1 }}>
            <IconButton size="large" aria-label="app menu" onClick={handleOpenNavMenu} color="inherit" sx={{ mr: 1 }}>
              <MenuIcon />
            </IconButton>
            <MovieIcon sx={{ fontSize: 28, color: 'primary.main', mr: 1 }} />
            <Typography
              variant="h6"
              component={Link}
              to="/"  // Dashboard'a yönlendir
              sx={{ fontWeight: 700, color: 'text.primary', textDecoration: 'none', fontSize: '1.2rem', '&:hover': { color: 'primary.main' } }}
            >
              MOVIE MOOD
            </Typography>
          </Box>
        </Box>

        {/* Orta Menü */}
        <Box sx={{ display: { xs: 'none', md: 'flex' }, justifyContent: 'center', flexGrow: 1, gap: 1 }}>
          {isLoggedIn && navItems.map(item => (
            <Button key={item.label} component={Link} to={item.path} sx={{ color: 'text.primary', fontWeight: 500, px: 2, '&:hover': { bgcolor: 'primary.light', color: 'white' } }}>
              {item.label}
            </Button>
          ))}
        </Box>

        {/* Sağ Menü */}
        <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center' }}>
          {isLoggedIn ? (
            <Button onClick={handleLogout} variant="outlined" sx={{ borderColor: 'secondary.main', color: 'secondary.main', '&:hover': { bgcolor: 'secondary.main', color: 'white' } }}>
              Çıkış Yap
            </Button>
          ) : (
            <>
              <Button component={Link} to="/login">Giriş Yap</Button>
              <Button component={Link} to="/register" variant="contained">Kayıt Ol</Button>
            </>
          )}
        </Box>

        {/* Mobil Menü */}
        <Menu anchorEl={anchorElNav} open={Boolean(anchorElNav)} onClose={handleCloseNavMenu} sx={{ display: { xs: 'block', md: 'none' } }}>
          {isLoggedIn && navItems.map(item => (
            <MenuItem key={item.label} onClick={handleCloseNavMenu} component={Link} to={item.path}>
              <Typography>{item.label}</Typography>
            </MenuItem>
          ))}
          <MenuItem onClick={isLoggedIn ? handleLogout : () => navigate('/login')}>
            <Typography>{isLoggedIn ? 'Çıkış Yap' : 'Giriş Yap'}</Typography>
          </MenuItem>
        </Menu>

      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
