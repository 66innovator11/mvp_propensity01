import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from './theme';
import UploadPage from './components/UploadPage';
import ClusterAnalysis from './components/ClusterAnalysis';
import ClusterDetailsPage from './components/ClusterDetailsPage';
import ReviewEmailsPage from './components/ReviewEmailsPage';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/cluster-analysis" element={<ClusterAnalysis />} />
          <Route path="/cluster-details/:productName" element={<ClusterDetailsPage />} />
          <Route path="/review-emails" element={<ReviewEmailsPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
