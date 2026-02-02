import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Card,
  CardContent,
  Button,
  Box,
  TextField,
  Container,
  Snackbar,
  Alert
} from '@mui/material';
import { apiService } from '../services/api';

const UploadPage: React.FC = () => {
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [showSuccessPopup, setShowSuccessPopup] = useState(false);
  const [isPipelineRunning, setIsPipelineRunning] = useState(false);
  const navigate = useNavigate();

  // Actual function for uploading files to GCS via backend
  const uploadFiles = async (files: FileList): Promise<void> => {
    console.log('Creating FormData...');
    
    try {
      const result = await apiService.uploadFiles(files);
      console.log('Upload successful:', result);
    } catch (error) {
      console.error('Upload failed:', error);
      throw error;
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length <= 4) {
      setSelectedFiles(files);
    } else {
      alert('Please select up to 4 files only');
      event.target.value = '';
    }
  };

  const handleUpload = async () => {
    if (!selectedFiles) {
      console.log('No files selected');
      return;
    }

    console.log('Starting upload for files:', selectedFiles);
    
    setIsUploading(true);
    try {
      await uploadFiles(selectedFiles);
      console.log('Upload completed successfully');
      setUploadSuccess(true);
      setShowSuccessPopup(true); // Show success popup
    } catch (error) {
      console.error('Upload failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      alert(`Upload failed: ${errorMessage}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRunPipeline = async () => {
    console.log('Running pipeline...');
    setIsPipelineRunning(true);
    
    try {
      console.log('Calling pipeline endpoint...');
      const result = await apiService.runPipeline();
      console.log('Pipeline completed successfully:', result);

      // Show success message
      alert(`Pipeline executed successfully! Analyzed ${result.total_products_analyzed} products in ${result.execution_time}`);

      // Navigate to cluster analysis page
      navigate('/cluster-analysis', { state: { clusterData: result.cluster_results } });
      
    } catch (error) {
      console.error('Pipeline execution failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      alert(`Pipeline execution failed: ${errorMessage}`);
    } finally {
      setIsPipelineRunning(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* AppBar with title and logo */}
      <AppBar position="static">
        <Toolbar>
          <Box
            component="img"
            src="/images/download.jpg"
            alt="Logo"
            sx={{ height: 40, mr: 2 }}
          />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, textAlign: 'center' }}>
            Propensity to Buy
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main content with centered card */}
      <Container maxWidth="sm" sx={{ mt: 8 }}>
        <Card sx={{ p: 4, boxShadow: 3 }}>
          <CardContent>
            <Typography variant="h5" component="h2" gutterBottom align="center">
              Upload Files
            </Typography>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {/* File upload input */}
              <TextField
                type="file"
                inputProps={{
                  multiple: true,
                  accept: '*/*'
                }}
                onChange={handleFileChange}
                variant="outlined"
                helperText="Select up to 4 files"
              />

              {/* Display selected files */}
              {selectedFiles && (
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Selected files:
                  </Typography>
                  {Array.from(selectedFiles).map((file, index) => (
                    <Typography key={index} variant="body2">
                      {file.name} ({(file.size / 1024).toFixed(2)} KB)
                    </Typography>
                  ))}
                </Box>
              )}

              {/* Upload button */}
              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={!selectedFiles || isUploading}
                fullWidth
                sx={{ py: 1.5 }}
              >
                {isUploading ? 'Uploading...' : 'Send Data to GCS Bucket'}
              </Button>

              {/* Run Pipeline button */}
              <Button
                variant="contained"
                onClick={handleRunPipeline}
                disabled={!uploadSuccess || isPipelineRunning}
                color="secondary"
                fullWidth
                sx={{ py: 1.5 }}
              >
                {isPipelineRunning ? 'Running Pipeline...' : 'Run Pipeline'}
              </Button>

              {/* Success message removed - now using popup */}
            </Box>
          </CardContent>
        </Card>
      </Container>

      {/* Success Popup */}
      <Snackbar
        open={showSuccessPopup}
        autoHideDuration={6000}
        onClose={() => setShowSuccessPopup(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setShowSuccessPopup(false)} 
          severity="success" 
          sx={{ width: '100%' }}
        >
          Files uploaded successfully to Google Cloud Storage!
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default UploadPage;
