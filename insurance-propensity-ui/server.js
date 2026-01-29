const express = require('express');
const cors = require('cors');
const multer = require('multer');
const { Storage } = require('@google-cloud/storage');
const path = require('path');
require('dotenv').config();

// Set up Google Cloud authentication
// If GOOGLE_APPLICATION_CREDENTIALS is not set, use the service account JSON file in the project
if (!process.env.GOOGLE_APPLICATION_CREDENTIALS) {
  const serviceAccountPath = path.join(__dirname, 'propensity-to-buy-b7bde-d603e877bf61.json');
  process.env.GOOGLE_APPLICATION_CREDENTIALS = serviceAccountPath;
}

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Multer configuration for handling file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 100 * 1024 * 1024, // 100MB limit
  },
});

// Initialize GCP Storage
const projectId = process.env.GCP_PROJECT_ID || 'propensity-to-buy-b7bde';
const bucketName = process.env.GCP_BUCKET_NAME || 'cust_data_bucket';

let storage;
try {
  storage = new Storage({
    projectId: projectId,
  });
  console.log('✓ GCP Storage initialized successfully');
} catch (error) {
  console.error('✗ Failed to initialize GCP Storage:', error.message);
  console.error('Make sure GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly');
}

const bucket = storage.bucket(bucketName);

// Root endpoint - shows server status
app.get('/', (req, res) => {
  res.json({
    status: '✓ Server is running',
    message: 'Backend server for Insurance Propensity to Protect',
    endpoints: {
      health: '/api/health',
      upload: 'POST /api/upload',
      files: 'GET /api/files',
    },
    gcp: {
      projectId: projectId,
      bucket: bucketName,
    },
    usage: 'This server is meant to be called from the React frontend at http://localhost:3000',
  });
});

// Upload endpoint
app.post('/api/upload', upload.array('files', 4), async (req, res) => {
  try {
    console.log('\n📤 Upload request received');
    console.log(`Files count: ${req.files ? req.files.length : 0}`);
    
    if (!req.files || req.files.length === 0) {
      console.log('❌ No files provided in request');
      return res.status(400).json({ error: 'No files provided' });
    }

    if (!storage || !bucket) {
      console.log('❌ GCP Storage not initialized');
      return res.status(500).json({ 
        error: 'GCP Storage not initialized',
        details: 'Failed to initialize Google Cloud Storage. Check credentials and bucket configuration.'
      });
    }

    const uploadedFiles = [];

    // Upload each file to GCP
    for (const file of req.files) {
      try {
        const timestamp = new Date().getTime();
        const fileName = `uploads/${timestamp}_${file.originalname}`;
        
        console.log(`📝 Uploading: ${fileName}`);
        
        const fileUpload = bucket.file(fileName);

        await fileUpload.save(file.buffer, {
          metadata: {
            contentType: file.mimetype,
          },
        });

        uploadedFiles.push({
          name: file.originalname,
          path: fileName,
          size: file.size,
          timestamp: new Date().toISOString(),
        });

        console.log(`✓ Successfully uploaded: ${fileName}`);
      } catch (fileError) {
        console.error(`❌ Error uploading file ${file.originalname}:`, fileError.message);
        throw fileError;
      }
    }

    console.log(`✓ All ${uploadedFiles.length} file(s) uploaded successfully\n`);

    res.json({
      success: true,
      message: `Successfully uploaded ${uploadedFiles.length} file(s)`,
      files: uploadedFiles,
    });
  } catch (error) {
    console.error('❌ Upload error:', error.message);
    console.error('Details:', error);
    res.status(500).json({
      error: 'Failed to upload files',
      details: error.message,
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'Server is running' });
});

// List uploaded files endpoint
app.get('/api/files', async (req, res) => {
  try {
    const [files] = await bucket.getFiles({ prefix: 'uploads/' });
    
    const fileList = files.map((file) => ({
      name: file.name.split('/').pop(),
      path: file.name,
      size: file.metadata.size,
      created: file.metadata.timeCreated,
    }));

    res.json({
      success: true,
      files: fileList,
    });
  } catch (error) {
    console.error('Error listing files:', error);
    res.status(500).json({
      error: 'Failed to list files',
      details: error.message,
    });
  }
});

const PORT = process.env.PORT || 3001;

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
  console.log(`GCP Project ID: ${projectId}`);
  console.log(`GCP Bucket: ${bucketName}`);
  console.log('Make sure GOOGLE_APPLICATION_CREDENTIALS is set to your service account JSON file');
});
