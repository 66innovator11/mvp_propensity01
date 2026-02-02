# Cluster Analysis Drill-Down Functionality

## Overview
Complete drill-down system for insurance product cluster analysis with customer details view.

## Architecture
- **Frontend**: React + TypeScript + Material UI with routing
- **Backend**: FastAPI with customer data endpoints
- **API Service**: Centralized API communication layer
- **Components**: Modular, reusable React components

## Features

### 1. Cluster Analysis Dashboard
- **6 Insurance Product Cards**: Term Life, Critical Illness, Annuity, Endowment, Unit Linked, Whole Life
- **Click-to-Drill-Down**: Each card is clickable and navigates to customer details
- **Visual Feedback**: Hover effects and cursor pointer for better UX
- **Dynamic Images**: Unique cluster graphs for each product

### 2. Customer Details Page
- **Dynamic Title**: "Customer Details for {ProductName}"
- **Comprehensive Table**: 10 columns of customer information
- **Material UI Table**: Professional, sortable, responsive design
- **Navigation**: Back button to return to cluster analysis

### 3. Backend Integration
- **New Endpoint**: `/cluster-details/{productName}` 
- **Dynamic Data**: Different customer counts and profiles per product
- **Realistic Data**: Sample customer information with proper formatting
- **Error Handling**: Comprehensive error management

## API Endpoints

### New Endpoint
- `GET /cluster-details/{productName}` - Returns customer details for specific product

### Existing Endpoints
- `POST /upload` - Upload files to GCS bucket
- `POST /run-pipeline` - Execute analysis pipeline
- `GET /health` - Health check endpoint
- `GET /test` - Connectivity test endpoint

### Frontend Routes
- `/` - Upload page
- `/cluster-analysis` - Cluster analysis dashboard
- `/cluster-details/:productName` - Customer details page

## Customer Data Structure

### Table Columns
1. **Customer ID** - Unique identifier (CUST000001 format)
2. **Name** - Full customer name
3. **Address** - Complete address with city, state, ZIP
4. **Propensity Score** - 0.000 to 1.000 with color coding
5. **Insurance Product** - Product name
6. **Existing Products** - List of current insurance products
7. **Age** - Customer age (25-65)
8. **Annual Income** - Formatted income ($50,000 - $200,000)
9. **Risk Profile** - Low/Medium/High with color coding
10. **Contact** - Email and phone icons with tooltips

### Data Generation
- **Different Customer Counts**: Varies by product type
- **Propensity Scores**: Product-specific ranges
- **Realistic Profiles**: Proper names, addresses, contact info
- **Existing Products**: Random selection from insurance types

## Component Structure

### Frontend Components
```
src/
├── components/
│   ├── UploadPage.tsx              # File upload and pipeline execution
│   ├── ClusterAnalysis.tsx         # Product cards with drill-down
│   └── ClusterDetailsPage.tsx       # Customer details table
├── services/
│   └── api.ts                      # Centralized API service
└── App.tsx                         # Routing configuration
```

### Backend Structure
```
backend/
├── main.py                         # FastAPI application
│   ├── /cluster-details/{product}  # New customer details endpoint
│   ├── generate_sample_customer_data()  # Data generation function
│   └── existing endpoints...
└── requirements.txt                # Python dependencies
```

## User Flow

### Complete Journey
1. **Upload Files** → Select and upload customer data files
2. **Run Pipeline** → Execute propensity analysis
3. **View Clusters** → See 6 product cards with cluster visualizations
4. **Click Product** → Navigate to customer details for that product
5. **View Customers** → Browse detailed customer information table
6. **Navigate Back** → Return to cluster analysis

### URL Structure
- `/cluster-details/term-life` → Term Life customers
- `/cluster-details/critical-illness` → Critical Illness customers
- `/cluster-details/annuity` → Annuity customers
- `/cluster-details/endowment` → Endowment customers
- `/cluster-details/unit-linked` → Unit Linked customers
- `/cluster-details/whole-life` → Whole Life customers

## API Service Features

### Centralized Communication
- **Single Instance**: `apiService` singleton for all API calls
- **Error Handling**: Consistent error management
- **Type Safety**: TypeScript interfaces for all responses
- **Reusable**: Used across all components

### Available Methods
- `uploadFiles(files: FileList)` - Upload files to backend
- `runPipeline()` - Execute analysis pipeline
- `getClusterDetails(productName: string)` - Get customer details
- `testConnectivity()` - Test backend connection
- `healthCheck()` - Check backend health

## Material UI Features

### Table Styling
- **Header**: Green background with white text
- **Rows**: Alternating colors for readability
- **Chips**: Color-coded propensity scores and risk profiles
- **Icons**: Email and phone contact buttons with tooltips
- **Responsive**: Adapts to different screen sizes

### Navigation
- **AppBar**: Consistent header with back button
- **Buttons**: Material UI styled navigation
- **Loading States**: Circular progress indicators
- **Error States**: Alert components for errors

## Data Visualization

### Color Coding
- **Propensity Score**: 
  - Green (≥0.8): High propensity
  - Yellow (0.6-0.8): Medium propensity  
  - Red (<0.6): Low propensity
- **Risk Profile**:
  - Green: Low risk
  - Yellow: Medium risk
  - Red: High risk

### Customer Count by Product
- **Term Life**: 25 customers
- **Critical Illness**: 20 customers
- **Annuity**: 15 customers
- **Endowment**: 18 customers
- **Unit Linked**: 12 customers
- **Whole Life**: 22 customers

## Setup Instructions

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
py -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### Frontend Setup
```bash
cd propensity-frontend
npm install
npm start
```

### Test the Flow
1. Start both servers
2. Upload sample files
3. Run pipeline
4. Click on any product card
5. View customer details
6. Navigate back and try other products

## Future Enhancements

### Backend
- **Real Report Integration**: Parse actual report files
- **Database Integration**: Store customer data in database
- **Advanced Filtering**: Add query parameters for filtering
- **Export Functionality**: CSV/PDF export options

### Frontend
- **Advanced Filtering**: Search and filter customer table
- **Sorting**: Sort by any column
- **Pagination**: Handle large customer lists
- **Customer Profiles**: Individual customer detail pages

### Data Features
- **Real-time Updates**: WebSocket for live data
- **Advanced Analytics**: Customer segmentation insights
- **Integration**: CRM system integration
- **Reporting**: Automated report generation

## Technologies Used

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Material UI** - Component library
- **React Router** - Navigation
- **Axios-style API** - HTTP communication

### Backend
- **FastAPI** - Python web framework
- **Pydantic** - Data validation
- **Random Data Generation** - Sample data creation
- **CORS** - Cross-origin resource sharing

The complete drill-down system provides a professional, scalable solution for insurance product cluster analysis with detailed customer insights! 🎉
