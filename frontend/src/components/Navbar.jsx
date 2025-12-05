import React, { useState, useEffect } from 'react';
import {
  AppBar, Toolbar, Typography, Button, Box, IconButton,
  Menu, MenuItem, Dialog, DialogActions, DialogContent,
  DialogContentText, DialogTitle
} from '@mui/material';
import MovieIcon from '@mui/icons-material/Movie';
import MenuIcon from '@mui/icons-material/Menu';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();

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

  // Çıkış Onay Dialog state
  const [logoutDialogOpen, setLogoutDialogOpen] = useState(false);

  const handleLogoutClick = () => {
    setLogoutDialogOpen(true);
  };

  const confirmLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");

    window.dispatchEvent(new Event("loginStatusChanged"));

    setIsLoggedIn(false);
    setLogoutDialogOpen(false);
    navigate("/login");
  };

  const cancelLogout = () => {
    setLogoutDialogOpen(false);
  };

  const navItems = [
    { label: 'Mood Seçimi', path: '/mood' },
    { label: 'Önerilenler', path: '/movies' },
    { label: 'Geçmişim', path: '/history' },
  ];

  return (
    <>
      <AppBar position="sticky" sx={{ bgcolor: 'background.paper', boxShadow: 3 }}>
        <Toolbar sx={{ justifyContent: 'space-between', minHeight: { xs: 64, md: 70 } }}>
          
          {/* Sol Logo */}
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: { xs: 1, md: 0 } }}>
            <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', mr: 3 }}>
              <MovieIcon sx={{ fontSize: 32, color: 'primary.main', mr: 1.5 }} />
              <Typography
                variant="h5"
                component={Link}
                to="/dashboard"
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
              <IconButton onClick={handleOpenNavMenu} color="inherit" sx={{ mr: 1 }}>
                <MenuIcon />
              </IconButton>
              <MovieIcon sx={{ fontSize: 28, color: 'primary.main', mr: 1 }} />
              <Typography
                variant="h6"
                component={Link}
                to="/"
                sx={{ fontWeight: 700, color: 'text.primary', textDecoration: 'none' }}
              >
                MOVIE MOOD
              </Typography>
            </Box>
          </Box>

          {/* Orta Menü */}
          {/* Orta Menü */}
<Box sx={{ display: { xs: 'none', md: 'flex' }, justifyContent: 'center', flexGrow: 1, gap: 1 }}>
  {isLoggedIn && navItems.map(item => (
    <Button
      key={item.label}
      component={Link}
      to={item.path}
      sx={{
        color: location.pathname === item.path ? 'primary.main' : 'text.primary',
        fontWeight: location.pathname === item.path ? 700 : 500,
        borderBottom: location.pathname === item.path ? '3px solid #7c4dff' : '3px solid transparent',
        borderRadius: 0,
        px: 2,
        '&:hover': {
          bgcolor: 'primary.light',
          color: 'white',
        }
      }}
    >
      {item.label}
    </Button>
  ))}
</Box>


          {/* Sağ Menü */}
          <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
            {isLoggedIn ? (
              <Button variant="outlined" onClick={handleLogoutClick}>
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
          <Menu anchorEl={anchorElNav} open={Boolean(anchorElNav)} onClose={handleCloseNavMenu}>
            {isLoggedIn && navItems.map(item => (
              <MenuItem key={item.label} onClick={handleCloseNavMenu} component={Link} to={item.path}>
                <Typography>{item.label}</Typography>
              </MenuItem>
            ))}
            <MenuItem onClick={isLoggedIn ? handleLogoutClick : () => navigate('/login')}>
              <Typography>{isLoggedIn ? 'Çıkış Yap' : 'Giriş Yap'}</Typography>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Çıkış Onay Dialog */}
      <Dialog open={logoutDialogOpen} onClose={cancelLogout}>
        <DialogTitle>Çıkış Yap</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Uygulamadan çıkış yapmak istediğinize emin misiniz?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={cancelLogout}>Hayır</Button>
          <Button onClick={confirmLogout} color="error" variant="contained">Evet</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default Navbar;
