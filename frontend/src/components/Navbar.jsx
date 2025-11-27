import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, IconButton, Menu, MenuItem } from '@mui/material';
import MovieIcon from '@mui/icons-material/Movie';
import MenuIcon from '@mui/icons-material/Menu';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();

  // 🔥 TOKEN'A GÖRE GİRİŞ DURUMU
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return !!localStorage.getItem("token");
  });

  // Login'den dönünce Navbar güncellensin
  useEffect(() => {
    const checkLogin = () => {
      setIsLoggedIn(!!localStorage.getItem("token"));
    };
    window.addEventListener("storage", checkLogin);
    return () => window.removeEventListener("storage", checkLogin);
  }, []);

  // Mobil menü kontrolü
  const [anchorElNav, setAnchorElNav] = useState(null);

  const handleOpenNavMenu = (event) => {
    setAnchorElNav(event.currentTarget);
  };

  const handleCloseNavMenu = () => {
    setAnchorElNav(null);
  };

  // Çıkış butonu
  const handleLogout = () => {
  localStorage.removeItem("token");
  window.location.href = "/login";
};


  // Gösterilecek menü seçenekleri
  const navItems = [
    { label: 'Mood Seçimi', path: '/' },
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
              to="/"
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

          {/* Mobil Menü Butonu */}
          <Box sx={{ display: { xs: 'flex', md: 'none' }, alignItems: 'center', flexGrow: 1 }}>
            <IconButton
              size="large"
              aria-label="app menu"
              onClick={handleOpenNavMenu}
              color="inherit"
              sx={{ mr: 1 }}
            >
              <MenuIcon />
            </IconButton>

            <MovieIcon sx={{ fontSize: 28, color: 'primary.main', mr: 1 }} />
            <Typography
              variant="h6"
              component={Link}
              to="/"
              sx={{
                fontWeight: 700,
                color: 'text.primary',
                textDecoration: 'none',
                fontSize: '1.2rem',
                '&:hover': { color: 'primary.main' }
              }}
            >
              MOVIE MOOD
            </Typography>
          </Box>
        </Box>

        {/* Orta Menü (Masaüstü) */}
        <Box sx={{ 
          display: { xs: 'none', md: 'flex' },
          justifyContent: 'center',
          flexGrow: 1,
          gap: 1
        }}>
          {isLoggedIn && navItems.map((item) => (
            <Button
              key={item.label}
              component={Link}
              to={item.path}
              sx={{
                color: 'text.primary',
                fontWeight: 500,
                px: 2,
                '&:hover': {
                  bgcolor: 'primary.light',
                  color: 'white'
                }
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>

        {/* Sağ Menü (Login/Logout) */}
        <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center' }}>
          {isLoggedIn ? (
            <Button 
              onClick={handleLogout}
              variant="outlined"
              sx={{
                borderColor: 'secondary.main',
                color: 'secondary.main',
                '&:hover': {
                  bgcolor: 'secondary.main',
                  color: 'white'
                }
              }}
            >
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
        <Menu
          id="menu-appbar"
          anchorEl={anchorElNav}
          open={Boolean(anchorElNav)}
          onClose={handleCloseNavMenu}
          sx={{ display: { xs: 'block', md: 'none' } }}
        >
          {isLoggedIn && navItems.map((item) => (
            <MenuItem
              key={item.label}
              onClick={handleCloseNavMenu}
              component={Link}
              to={item.path}
            >
              <Typography>{item.label}</Typography>
            </MenuItem>
          ))}

          <MenuItem
            onClick={isLoggedIn ? handleLogout : () => navigate('/login')}
          >
            <Typography>{isLoggedIn ? 'Çıkış Yap' : 'Giriş Yap'}</Typography>
          </MenuItem>
        </Menu>

      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
