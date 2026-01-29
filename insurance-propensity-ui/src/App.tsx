import React from 'react';
import './App.css';
import FileUploadCard from './components/FileUploadCard';
import ClustersView from './components/ClustersView';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Box, AppBar, Toolbar, Button, Typography } from '@mui/material';

function App() {
  return (
    <BrowserRouter>
      <AppBar position="static" sx={{ backgroundColor: '#2e7d32' }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flex: 1 }}>Propensity to Buy</Typography>
          <Button color="inherit" component={Link} to="/">Upload</Button>
          <Button color="inherit" component={Link} to="/clusters">Clusters</Button>
        </Toolbar>
      </AppBar>

      <Box>
        <Routes>
          <Route path="/" element={<FileUploadCard />} />
          <Route path="/clusters" element={<ClustersView />} />
        </Routes>
      </Box>
    </BrowserRouter>
  );
}

export default App;
