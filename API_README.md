# Propensity Analysis API

This document describes the REST API for the propensity analysis system.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the API server:**
   ```bash
   cd src
   python run_api.py
   ```

3. **Open the web UI:**
   - Navigate to `src/static/index.html` in your browser
   - Or open `http://localhost:8000` for API documentation

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Health & Status

#### GET `/`
Root endpoint - returns basic API info.

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "success": true,
  "message": "API is healthy"
}
```

### Job Management

#### GET `/jobs`
List all jobs.

**Response:**
```json
[
  {
    "job_id": "uuid",
    "status": "completed|running|pending|failed",
    "progress": 0.0-1.0,
    "message": "Status message",
    "result": {...},
    "error": "Error message if failed",
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
]
```

#### GET `/jobs/{job_id}`
Get specific job status.

### Data Upload

#### POST `/upload-data`
Upload CSV data files.

**Form Data:**
- `customer_profile`: CSV file (required)
- `insurance_products`: CSV file (required)
- `transactions`: CSV file (required)
- `customer_events`: CSV file (optional)

**Response:**
```json
{
  "success": true,
  "message": "Data uploaded successfully",
  "data": {
    "upload_dir": "/path/to/uploads",
    "files": ["customer_profile.csv", ...]
  }
}
```

### Analysis Operations

#### POST `/clustering/start`
Start customer clustering analysis.

**Request Body:**
```json
{
  "k_min": 2,
  "k_max": 10,
  "random_state": 42
}
```

**Response:**
```json
{
  "success": true,
  "message": "Clustering analysis started",
  "data": {
    "job_id": "uuid"
  }
}
```

#### POST `/training/start`
Start propensity model training.

**Request Body:**
```json
{
  "random_state": 42
}
```

#### POST `/explain/start`
Start auto-explanation generation.

#### POST `/summarize/start`
Start propensity summarization.

#### POST `/outreach/start`
Start personalized outreach generation.

**Request Body:**
```json
{
  "sample_size": 10,
  "use_llm": false,
  "model": "gpt-3.5-turbo"
}
```

#### POST `/pipeline/start`
Start the complete analysis pipeline.

**Request Body:**
```json
{
  "clustering_request": {
    "k_min": 2,
    "k_max": 10,
    "random_state": 42
  },
  "training_request": {
    "random_state": 42
  },
  "outreach_request": {
    "sample_size": 10,
    "use_llm": false,
    "model": "gpt-3.5-turbo"
  }
}
```

### Results

#### GET `/results/clustering`
Get clustering analysis results.

**Response:**
```json
{
  "success": true,
  "message": "Clustering results retrieved",
  "data": {
    "metrics": [...],
    "profiles": {
      "product agnostic cluster profile": [...],
      "product wise cluster profile whole life": [...],
      "product wise cluster profile term life": [...]
    }
  }
}
```

#### GET `/results/propensity`
Get propensity analysis results.

**Response:**
```json
{
  "success": true,
  "message": "Propensity results retrieved",
  "data": {
    "combined_scores": [...],
    "summary": [...],
    "rationale": [...]
  }
}
```

#### GET `/results/outreach`
Get outreach generation results.

**Response:**
```json
{
  "success": true,
  "message": "Outreach results retrieved",
  "data": {
    "outreach_file_name": [...]
  }
}
```

## Web UI

The web interface provides a user-friendly way to interact with the API:

1. **Data Upload**: Upload CSV files through a web form
2. **Analysis Controls**: Configure and start analysis operations
3. **Job Monitoring**: Track progress of running jobs
4. **Results Viewing**: View and download analysis results

### Using the Web UI

1. Open `src/static/index.html` in your browser
2. Upload your data files using the form
3. Configure analysis parameters
4. Start individual operations or the full pipeline
5. Monitor job progress in real-time
6. View results when completed

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Resource not found
- `500`: Internal server error

## Rate Limiting

Currently, no rate limiting is implemented. Consider adding rate limiting for production use.

## Security Considerations

1. **CORS**: Currently allows all origins - configure appropriately for production
2. **File Uploads**: Validate file types and sizes in production
3. **Authentication**: No authentication implemented - add for production use

## Development

### Running in Development Mode

```bash
cd src
python run_api.py
```

The server will auto-reload when code changes are detected.

### API Documentation

When the server is running, visit:
- `http://localhost:8000/docs` for interactive API documentation (Swagger UI)
- `http://localhost:8000/redoc` for alternative documentation (ReDoc)

## Production Deployment

For production deployment:

1. Use a production-grade ASGI server like Gunicorn with Uvicorn workers
2. Implement proper authentication and authorization
3. Configure CORS appropriately
4. Add logging and monitoring
5. Set up proper file storage for uploads and results
6. Consider containerization with Docker

Example production command:
```bash
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
