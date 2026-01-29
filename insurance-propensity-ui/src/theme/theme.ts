import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },   // Blue for Life Insurance
    secondary: { main: '#2e7d32' }, // Green for Health Insurance
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
    h6: { fontWeight: 600 },
  },
});

export default theme;