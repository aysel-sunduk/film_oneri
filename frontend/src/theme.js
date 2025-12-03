// src/theme.js
import { createTheme } from '@mui/material/styles';
import { purple, deepPurple } from '@mui/material/colors';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: purple[500], light: purple[300], dark: purple[700] },
    secondary: { main: deepPurple['A200'], light: deepPurple['A100'], dark: deepPurple['A400'] },
    background: { default: '#1C1625', paper: '#282033' },
    text: { primary: '#ffffff', secondary: '#E0B0FF' },
    error: { main: '#FF4444' }
  },
  typography: {
    fontFamily: ['Roboto', '"Helvetica Neue"', 'Arial', 'sans-serif'].join(',')
  },
  components: {
    MuiCard: { styleOverrides: { root: { borderRadius: 10, backgroundColor: '#282033' } } },
    MuiButton: { styleOverrides: { root: { textTransform: 'none' } } },
  },
});

export default theme;
