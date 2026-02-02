# FastAPI File Upload Backend

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Google Cloud Setup

#### Create Service Account:
1. Go to Google Cloud Console
2. Navigate to IAM & Admin > Service Accounts
3. Create a new service account
4. Download the JSON key file

#### Set Environment Variable:
**Windows:**
```cmd
set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\service-account-key.json"
```

**Linux/Mac:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

#### Create GCS Bucket:
1. Go to Google Cloud Storage
2. Create a new bucket
3. Update `BUCKET_NAME` in `main.py` with your bucket name

### 3. Run the Server
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

## API Endpoints

### POST /upload
Upload multiple files to Google Cloud Storage

**Request:** 
- Content-Type: multipart/form-data
- Files: List of files to upload

**Response:**
```json
{
  "message": "File upload completed",
  "uploaded_files": [
    {
      "original_filename": "example.txt",
      "gcs_filename": "uuid_example.txt",
      "public_url": "https://storage.googleapis.com/bucket-name/uuid_example.txt",
      "size": 1024
    }
  ],
  "total_uploaded": 1,
  "total_files": 1
}
```

### GET /health
Check server health and GCS configuration

### GET /
Root endpoint to verify server is running

## Testing with Frontend

The frontend should send files to `http://localhost:5000/upload` using FormData.

## Notes

- Files are stored with unique UUID prefixes to avoid naming conflicts
- Files are made publicly accessible after upload
- Error handling included for missing files and GCS configuration issues
