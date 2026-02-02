# Propensity to Buy - Cluster Analysis System

## Overview
Complete React + TypeScript + Material UI frontend with FastAPI backend for customer propensity analysis and cluster visualization.

## Architecture
- **Frontend**: React + TypeScript + Material UI (Port 3000)
- **Backend**: FastAPI + Python (Port 5000)
- **Storage**: Google Cloud Storage
- **Routing**: React Router for navigation

## Features

### 1. File Upload System
- Upload up to 4 files to Google Cloud Storage
- Real-time upload progress and success notifications
- Material UI components with Lloyds Bank green theme

### 2. Pipeline Execution
- Trigger propensity analysis pipeline
- Process uploaded files and generate cluster reports
- Simulated 3-second execution time

### 3. Cluster Analysis Dashboard
- Display 6 product cluster analyses in grid layout
- Show cluster visualizations and business insights
- Conversion potential indicators (High/Medium/Low)
- Customer count metrics

## API Endpoints

### Backend Endpoints
- `POST /upload` - Upload files to GCS bucket
- `POST /run-pipeline` - Execute analysis pipeline
- `GET /health` - Health check endpoint
- `GET /test` - Connectivity test endpoint

### Frontend Routes
- `/` - Upload page
- `/cluster-analysis` - Cluster analysis dashboard

## Product Categories
1. **Credit Cards** - High-value customer identification
2. **Personal Loans** - Personal financing targeting
3. **Mortgage Products** - Home financing solutions
4. **Investment Services** - Wealth management prospects
5. **Insurance Products** - Insurance cross-selling
6. **Savings Accounts** - High-yield savings opportunities

## Setup Instructions

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
# Set GOOGLE_APPLICATION_CREDENTIALS environment variable
py -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### Frontend Setup
```bash
cd propensity-frontend
npm install
npm start
```

### Environment Variables
```bash
# For Google Cloud Storage access
GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

## File Structure
```
test/
├── backend/
│   ├── main.py                 # FastAPI backend
│   ├── requirements.txt        # Python dependencies
│   └── README.md              # Backend documentation
├── propensity-frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadPage.tsx      # File upload component
│   │   │   └── ClusterAnalysis.tsx # Cluster analysis dashboard
│   │   ├── App.tsx             # Main app with routing
│   │   └── theme.ts            # Material UI theme
│   └── package.json
└── images/
    └── download.jpg           # Logo file
```

## Usage Flow
1. Upload customer data files
2. Click "Run Pipeline" to execute analysis
3. View cluster analysis results
4. Navigate between upload and analysis pages

## Future Enhancements
- Real cluster visualization images
- Actual pipeline execution logic
- Report folder parsing integration
- Advanced filtering and search
- Export functionality
- Real-time updates

## Technologies Used
- **Frontend**: React 19, TypeScript, Material UI, React Router
- **Backend**: FastAPI, Python, Google Cloud Storage
- **Styling**: Material UI with custom Lloyds Bank theme
- **Development**: Vite, ESLint, Prettier
