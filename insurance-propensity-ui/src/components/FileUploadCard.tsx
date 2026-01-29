import React, { useState } from 'react';
import { Box, Card, CardContent, Typography, Button, Container, List, ListItem, ListItemIcon, ListItemText, IconButton, TextField, Chip, LinearProgress } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ClearIcon from '@mui/icons-material/Clear';
import DescriptionIcon from '@mui/icons-material/Description';
import AddIcon from '@mui/icons-material/Add';

type UploadStatus = 'initial' | 'review' | 'predictors';

const FileUploadCard: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [fileNames, setFileNames] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('initial');
  const [predictors, setPredictors] = useState<string[]>([]);
  const [predictorInput, setPredictorInput] = useState<string>('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files?.length) {
      const newFilesArray = Array.from(event.target.files);
      // Only allow up to 4 files total
      const remainingSlots = 4 - files.length;
      const filesToAdd = newFilesArray.slice(0, remainingSlots);
      
      setFiles([...files, ...filesToAdd]);
      setFileNames([...fileNames, ...filesToAdd.map(file => file.name)]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
    setFileNames(fileNames.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setIsUploading(true);
    try {
      // Create FormData for multipart upload
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });

      console.log(`📤 Uploading ${files.length} file(s)...`);

      // Upload to backend API which will handle GCP upload
      const response = await fetch('http://localhost:3001/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          errorData = { details: `HTTP ${response.status}: ${response.statusText}` };
        }
        throw new Error(errorData.details || errorData.error || 'Upload failed');
      }

      const data = await response.json();
      console.log('✓ Upload response:', data);
      
      // Show success message and move to review
      alert(`✓ Successfully uploaded ${files.length} file(s) to GCP Cloud Storage!`);
      setUploadStatus('review');
    } catch (error) {
      console.error('❌ Upload failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(
        `❌ Upload failed: ${errorMessage}\n\n` +
        'Troubleshooting:\n' +
        '1. Check that backend server is running: npm run server\n' +
        '2. Verify GCP credentials are set up correctly\n' +
        '3. Check browser console (F12) for more details\n' +
        '4. Check server logs for error messages'
      );
    } finally {
      setIsUploading(false);
    }
  };

  const handleOpenFile = (fileName: string) => {
    const file = files.find(f => f.name === fileName);
    if (!file) return;

    // Create a blob URL and open based on file type
    const fileURL = URL.createObjectURL(file);
    const fileExtension = fileName.split('.').pop()?.toLowerCase();

    // Open in new tab - browser will handle Excel, CSV, PDF etc. natively
    window.open(fileURL, '_blank');

    // Clean up the URL after a delay to avoid issues
    setTimeout(() => {
      URL.revokeObjectURL(fileURL);
    }, 100);
  };

  const handleAddPredictor = () => {
    if (predictorInput.trim()) {
      setPredictors([...predictors, predictorInput.trim()]);
      setPredictorInput('');
    }
  };

  const handleRemovePredictor = (index: number) => {
    setPredictors(predictors.filter((_, i) => i !== index));
  };

  const handleBackToReview = () => {
    setUploadStatus('review');
  };

  const handleGoToPredictors = () => {
    setUploadStatus('predictors');
  };

  const handleReset = () => {
    setUploadStatus('initial');
    setFiles([]);
    setFileNames([]);
    setPredictors([]);
    setPredictorInput('');
  };

  // Calculate progress percentage (0%, 33%, 66%, 100%)
  const getProgressPercentage = () => {
    switch (uploadStatus) {
      case 'initial':
        return 33;
      case 'review':
        return 66;
      case 'predictors':
        return 100;
      default:
        return 0;
    }
  };

  // Get step number (1, 2, or 3)
  const getStepNumber = () => {
    switch (uploadStatus) {
      case 'initial':
        return 1;
      case 'review':
        return 2;
      case 'predictors':
        return 3;
      default:
        return 0;
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Header */}
      <Box
        sx={{
          backgroundColor: '#2e7d32',
          color: 'white',
          padding: '20px',
          textAlign: 'center',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 2,
        }}
      >
        <img
          src="/lloyds-logo.webp"
          alt="Lloyds Logo"
          style={{ height: '50px', width: 'auto' }}
        />
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          Propensity to Buy
        </Typography>
      </Box>

      {/* Main Content */}
      <Container
        maxWidth="sm"
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flex: 1,
          paddingY: 4,
        }}
      >
        <Card
          sx={{
            width: '100%',
            boxShadow: 3,
          }}
        >
          {/* Progress Bar Section */}
          <Box sx={{ padding: '20px', backgroundColor: '#f5f5f5' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
              <Box sx={{ textAlign: 'center', flex: 1 }}>
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    backgroundColor: uploadStatus === 'initial' || uploadStatus === 'review' || uploadStatus === 'predictors' ? '#2e7d32' : '#ccc',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 8px',
                    fontWeight: 'bold',
                  }}
                >
                  {uploadStatus === 'initial' ? '1' : <CheckCircleIcon sx={{ fontSize: 24 }} />}
                </Box>
                <Typography sx={{ fontSize: '12px', color: '#2e7d32', fontWeight: 'bold' }}>
                  Upload Files
                </Typography>
              </Box>

              <Box sx={{ textAlign: 'center', flex: 1 }}>
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    backgroundColor: uploadStatus === 'review' || uploadStatus === 'predictors' ? '#2e7d32' : '#ccc',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 8px',
                    fontWeight: 'bold',
                  }}
                >
                  {uploadStatus === 'predictors' ? <CheckCircleIcon sx={{ fontSize: 24 }} /> : '2'}
                </Box>
                <Typography sx={{ fontSize: '12px', color: uploadStatus === 'review' || uploadStatus === 'predictors' ? '#2e7d32' : '#999', fontWeight: 'bold' }}>
                  Review Data
                </Typography>
              </Box>

              <Box sx={{ textAlign: 'center', flex: 1 }}>
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    backgroundColor: uploadStatus === 'predictors' ? '#2e7d32' : '#ccc',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 8px',
                    fontWeight: 'bold',
                  }}
                >
                  3
                </Box>
                <Typography sx={{ fontSize: '12px', color: uploadStatus === 'predictors' ? '#2e7d32' : '#999', fontWeight: 'bold' }}>
                  Add Predictors
                </Typography>
              </Box>
            </Box>

            {/* Progress Bar */}
            <Box sx={{ position: 'relative', marginBottom: 1 }}>
              <LinearProgress
                variant="determinate"
                value={getProgressPercentage()}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  backgroundColor: '#e0e0e0',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: '#2e7d32',
                    borderRadius: 3,
                  },
                }}
              />
            </Box>
            
            <Typography sx={{ fontSize: '12px', color: '#666', textAlign: 'center' }}>
              Step {getStepNumber()} of 3
            </Typography>
          </Box>

          <CardContent
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 3,
              padding: 4,
              textAlign: 'center',
            }}
          >
            {/* Initial Upload View */}
            {uploadStatus === 'initial' && (
              <>
                <Typography variant="h5" sx={{ color: '#2e7d32', fontWeight: 'bold' }}>
                  Upload Customer Data
                </Typography>

                <CloudUploadIcon sx={{ fontSize: 80, color: '#2e7d32' }} />

                <Button
                  variant="contained"
                  component="label"
                  disabled={files.length >= 4}
                  sx={{
                    backgroundColor: '#2e7d32',
                    padding: '12px 32px',
                    fontSize: '16px',
                    '&:hover': {
                      backgroundColor: '#1b5e20',
                    },
                    '&:disabled': {
                      backgroundColor: '#ccc',
                    },
                  }}
                >
                  <CloudUploadIcon sx={{ marginRight: 1 }} />
                  Choose File ({files.length}/4)
                  <input type="file" hidden onChange={handleFileChange} multiple />
                </Button>

                {files.length > 0 && (
                  <Box
                    sx={{
                      padding: 2,
                      backgroundColor: '#e8f5e9',
                      borderRadius: 1,
                      border: '2px solid #2e7d32',
                      width: '100%',
                    }}
                  >
                    <Typography sx={{ color: '#2e7d32', fontWeight: 'bold', marginBottom: 1 }}>
                      ✓ Files Selected ({files.length}/4):
                    </Typography>
                    <List sx={{ maxHeight: 300, overflow: 'auto' }}>
                      {fileNames.map((name, index) => (
                        <ListItem
                          key={index}
                          secondaryAction={
                            <IconButton
                              edge="end"
                              size="small"
                              onClick={() => removeFile(index)}
                              sx={{ color: '#2e7d32' }}
                            >
                              <ClearIcon fontSize="small" />
                            </IconButton>
                          }
                          sx={{ paddingY: 0.5 }}
                        >
                          <ListItemIcon sx={{ minWidth: 32, color: '#2e7d32' }}>
                            <CheckCircleIcon fontSize="small" />
                          </ListItemIcon>
                          <ListItemText
                            primary={name}
                            sx={{
                              '& .MuiListItemText-primary': {
                                color: '#2e7d32',
                                fontSize: '14px',
                                wordBreak: 'break-word',
                              },
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>

                    <Button
                      variant="contained"
                      fullWidth
                      disabled={isUploading}
                      onClick={handleUpload}
                      sx={{
                        marginTop: 2,
                        backgroundColor: '#2e7d32',
                        padding: '12px',
                        fontSize: '16px',
                        fontWeight: 'bold',
                        '&:hover': {
                          backgroundColor: '#1b5e20',
                        },
                        '&:disabled': {
                          backgroundColor: '#ccc',
                        },
                      }}
                    >
                      {isUploading ? 'Uploading...' : 'Upload Files'}
                    </Button>
                  </Box>
                )}
              </>
            )}

            {/* Review Data View */}
            {uploadStatus === 'review' && (
              <>
                <Typography variant="h5" sx={{ color: '#2e7d32', fontWeight: 'bold' }}>
                  Review Uploaded Data
                </Typography>

                <Box
                  sx={{
                    padding: 2,
                    backgroundColor: '#e8f5e9',
                    borderRadius: 1,
                    border: '2px solid #2e7d32',
                    width: '100%',
                  }}
                >
                  <Typography sx={{ color: '#2e7d32', fontWeight: 'bold', marginBottom: 2 }}>
                    📁 Files Uploaded ({fileNames.length}):
                  </Typography>
                  <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                    {fileNames.map((name, index) => (
                      <ListItem
                        key={index}
                        secondaryAction={
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleOpenFile(name)}
                            sx={{
                              borderColor: '#2e7d32',
                              color: '#2e7d32',
                              '&:hover': {
                                backgroundColor: '#e8f5e9',
                              },
                            }}
                          >
                            Open
                          </Button>
                        }
                        sx={{ paddingY: 1 }}
                      >
                        <ListItemIcon sx={{ minWidth: 32, color: '#2e7d32' }}>
                          <DescriptionIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary={name}
                          sx={{
                            '& .MuiListItemText-primary': {
                              color: '#2e7d32',
                              fontSize: '14px',
                              wordBreak: 'break-word',
                            },
                          }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>

                <Box sx={{ display: 'flex', gap: 2, width: '100%' }}>
                  <Button
                    variant="contained"
                    fullWidth
                    onClick={handleGoToPredictors}
                    sx={{
                      backgroundColor: '#2e7d32',
                      padding: '12px',
                      fontSize: '16px',
                      fontWeight: 'bold',
                      '&:hover': {
                        backgroundColor: '#1b5e20',
                      },
                    }}
                  >
                    Add Predictors
                  </Button>
                  <Button
                    variant="outlined"
                    fullWidth
                    onClick={handleReset}
                    sx={{
                      borderColor: '#2e7d32',
                      color: '#2e7d32',
                      padding: '12px',
                      fontSize: '16px',
                      fontWeight: 'bold',
                      '&:hover': {
                        backgroundColor: '#f0f0f0',
                      },
                    }}
                  >
                    Upload More Files
                  </Button>
                </Box>
              </>
            )}

            {/* Add Predictors View */}
            {uploadStatus === 'predictors' && (
              <>
                <Typography variant="h5" sx={{ color: '#2e7d32', fontWeight: 'bold' }}>
                  Add Predictors
                </Typography>

                <Typography sx={{ color: '#666', fontSize: '14px' }}>
                  Add relevant fields like High Salary, Age greater than 40, etc.
                </Typography>

                <Box sx={{ width: '100%', display: 'flex', gap: 1 }}>
                  <TextField
                    fullWidth
                    placeholder="Enter predictor (e.g., High Salary, Age > 40)"
                    value={predictorInput}
                    onChange={(e) => setPredictorInput(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleAddPredictor();
                      }
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '& fieldset': {
                          borderColor: '#2e7d32',
                        },
                        '&:hover fieldset': {
                          borderColor: '#1b5e20',
                        },
                      },
                    }}
                  />
                  <Button
                    variant="contained"
                    onClick={handleAddPredictor}
                    sx={{
                      backgroundColor: '#2e7d32',
                      padding: '12px 24px',
                      '&:hover': {
                        backgroundColor: '#1b5e20',
                      },
                    }}
                  >
                    <AddIcon />
                  </Button>
                </Box>

                {predictors.length > 0 && (
                  <Box
                    sx={{
                      padding: 2,
                      backgroundColor: '#e8f5e9',
                      borderRadius: 1,
                      border: '2px solid #2e7d32',
                      width: '100%',
                    }}
                  >
                    <Typography sx={{ color: '#2e7d32', fontWeight: 'bold', marginBottom: 1.5 }}>
                      Predictors Added ({predictors.length}):
                    </Typography>
                    <Box
                      sx={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: 1,
                      }}
                    >
                      {predictors.map((predictor, index) => (
                        <Chip
                          key={index}
                          label={predictor}
                          onDelete={() => handleRemovePredictor(index)}
                          sx={{
                            backgroundColor: '#2e7d32',
                            color: 'white',
                            fontWeight: 'bold',
                            '& .MuiChip-deleteIcon': {
                              color: 'white',
                              '&:hover': {
                                color: '#fff',
                              },
                            },
                          }}
                        />
                      ))}
                    </Box>
                  </Box>
                )}

                <Box sx={{ display: 'flex', gap: 2, width: '100%' }}>
                  <Button
                    variant="contained"
                    fullWidth
                    onClick={handleBackToReview}
                    sx={{
                      backgroundColor: '#2e7d32',
                      padding: '12px',
                      fontSize: '16px',
                      fontWeight: 'bold',
                      '&:hover': {
                        backgroundColor: '#1b5e20',
                      },
                    }}
                  >
                    Back to Review
                  </Button>
                  <Button
                    variant="outlined"
                    fullWidth
                    onClick={handleReset}
                    sx={{
                      borderColor: '#2e7d32',
                      color: '#2e7d32',
                      padding: '12px',
                      fontSize: '16px',
                      fontWeight: 'bold',
                      '&:hover': {
                        backgroundColor: '#f0f0f0',
                      },
                    }}
                  >
                    Analyze Data
                  </Button>
                </Box>
              </>
            )}
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default FileUploadCard;