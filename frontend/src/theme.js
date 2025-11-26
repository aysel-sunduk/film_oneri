import { createTheme } from '@mui/material/styles';
import { purple, deepPurple } from '@mui/material/colors';

const theme = createTheme({
  palette: {
    // 1. Temanın tipini 'dark' olarak belirleyelim
    mode: 'dark',
    
    // 2. Birincil (Primary) renk olarak morun derin tonlarını kullanalım
    primary: {
      // main: Uygulamanın temel rengi (butonlar, vurgular)
      main: purple[500], // MUI'nin hazır mor tonlarından 500
      light: purple[300],
      dark: purple[700],
    },
    
    // İkincil (Secondary) renk olarak daha derin veya farklı bir mor/mor-mavi kullanalım
    secondary: {
      main: deepPurple['A200'], // Daha parlak bir mor aksan rengi
      light: deepPurple['A100'],
      dark: deepPurple['A400'],
    },
    
    // 3. Koyu tema için arka plan renkleri
    background: {
      default: '#1C1625', // Derin mor-siyah arka plan
      paper: '#282033',  // Kartlar ve paneller için biraz daha açık arka plan
    },
    
    // 4. Metin rengi
    text: {
      primary: '#ffffff',
      secondary: '#E0B0FF', // Mor ile uyumlu açık mor/beyaz tonu
    },
    
    // Aksanlar için hata ve uyarı renkleri (isteğe bağlı)
    error: {
        main: '#FF4444',
    }
  },
  
  // 5. Tipografi (Yazı Tipleri)
  typography: {
    fontFamily: [
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },

  // 6. Bileşen Özelleştirmeleri
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          // Kart arka planını biraz daha belirgin hale getirelim
          backgroundColor: '#282033', 
        },
      },
    },
    MuiButton: {
        styleOverrides: {
            root: {
                textTransform: 'none', // Buton yazılarının büyük harf olmasını engeller
            },
        },
    },
  },
});

export default theme;