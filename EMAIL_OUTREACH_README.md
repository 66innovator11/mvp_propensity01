# Email Outreach Functionality

## Overview
Complete email outreach system for insurance products with draft generation, review, and approval workflow.

## Architecture
- **Frontend**: React + TypeScript + Material UI with email review system
- **Backend**: FastAPI with email template generation and management
- **Email Templates**: Product-specific personalized email content
- **Review Workflow**: Professional email approval process

## Features

### 1. Email Generation
- **Product-Specific Templates**: Unique email content for each insurance product
- **Personalization**: Customer name, propensity score, and agent assignment
- **Dynamic Content**: Based on customer profiles and product characteristics
- **Professional Formatting**: Business-appropriate email structure

### 2. Email Review System
- **Review Table**: Comprehensive list of all generated emails
- **Email Dialog**: Detailed email preview with customer information
- **Approval Workflow**: Approve or reject individual emails
- **Batch Operations**: Send approved emails in bulk

### 3. User Experience
- **Seamless Navigation**: From customer details to email generation
- **Loading States**: Professional feedback during email generation
- **Error Handling**: Comprehensive error management
- **Responsive Design**: Works on all screen sizes

## Email Templates by Product

### 1. Term Life Insurance
- **Focus**: Family protection and income replacement
- **Key Points**: Affordable premiums, tax-free benefits, peace of mind
- **Target Audience**: Young families, income earners

### 2. Critical Illness Insurance
- **Focus**: Medical expense coverage and income protection
- **Key Points**: Lump-sum payouts, recovery support, savings protection
- **Target Audience**: Health-conscious individuals, families

### 3. Annuity Products
- **Focus**: Retirement income and financial security
- **Key Points**: Guaranteed income, market protection, flexible options
- **Target Audience**: Pre-retirement and retired individuals

### 4. Endowment Policies
- **Focus**: Savings and protection combination
- **Key Points**: Guaranteed benefits, disciplined saving, tax advantages
- **Target Audience**: Long-term planners, savers

### 5. Unit Linked Insurance
- **Focus**: Investment-linked protection
- **Key Points**: Market returns, fund flexibility, growth potential
- **Target Audience**: Investors, risk-tolerant individuals

### 6. Whole Life Insurance
- **Focus**: Lifelong protection and wealth building
- **Key Points**: Lifetime coverage, cash value, estate planning
- **Target Audience**: High-net-worth individuals, estate planners

## API Endpoints

### New Endpoints
- `POST /send-emails/{productName}` - Generate draft emails for product
- `GET /review-emails` - Get all draft emails for review

### Existing Endpoints
- `GET /cluster-details/{productName}` - Customer details for email targeting
- `POST /upload` - File upload for customer data
- `POST /run-pipeline` - Analysis pipeline execution

### Frontend Routes
- `/` - Upload page
- `/cluster-analysis` - Product clusters
- `/cluster-details/:productName` - Customer details with email button
- `/review-emails` - Email review and approval

## Email Generation Process

### Backend Logic
1. **Product Identification**: Determine insurance product type
2. **Customer Selection**: Get high-propensity customers for product
3. **Template Selection**: Choose appropriate email template
4. **Personalization**: Add customer-specific details
5. **Agent Assignment**: Assign appropriate insurance agent
6. **Draft Generation**: Create personalized email content

### Email Content Structure
```
Subject: Product-specific compelling subject line

Dear [Customer Name],

[Personalized opening based on profile]

Why [Product Name] is Right for You:
• [Benefit 1]
• [Benefit 2]
• [Benefit 3]
• [Benefit 4]

Your Propensity Score: [Score]
[Explanation of score and relevance]

Next Steps:
[Call to action with specific agent]

Best regards,
[Agent Name]
[Agent Title]
Lloyds Bank Insurance Services
Contact: [Agent Contact]
```

## Component Structure

### Frontend Components
```
src/
├── components/
│   ├── UploadPage.tsx              # File upload and pipeline
│   ├── ClusterAnalysis.tsx         # Product cards
│   ├── ClusterDetailsPage.tsx      # Customer details + Send Emails button
│   ├── ReviewEmailsPage.tsx        # Email review table
│   └── EmailDialog.tsx             # Email preview dialog
├── services/
│   └── api.ts                      # API service with email methods
└── App.tsx                         # Routing with email routes
```

### Backend Structure
```
backend/
├── main.py                         # FastAPI application
│   ├── /send-emails/{product}      # Email generation endpoint
│   ├── /review-emails              # Email review endpoint
│   ├── generate_email_drafts()     # Email generation logic
│   └── existing endpoints...
└── requirements.txt                # Python dependencies
```

## User Workflow

### Complete Email Outreach Journey
1. **Upload Data** → **Run Pipeline** → **View Clusters**
2. **Click Product** → **View Customer Details**
3. **Click "Send Emails"** → **Generate Draft Emails**
4. **Navigate to Review** → **Review Email Table**
5. **Click "Review Email"** → **Preview in Dialog**
6. **Approve/Reject** → **Send Approved Emails**

### Email Generation Flow
1. **Product Selection**: User chooses product from customer details
2. **Customer Targeting**: System identifies high-propensity customers
3. **Template Matching**: Appropriate template selected
4. **Personalization**: Customer details inserted
5. **Agent Assignment**: Professional agent assigned
6. **Draft Creation**: Complete email generated

## Email Review Features

### Review Table
- **Customer Information**: ID, name, product, propensity score
- **Email Details**: Subject, agent, generation date, status
- **Actions**: Review button for each email
- **Sorting**: By propensity score (highest first)

### Email Dialog
- **Customer Header**: Name, ID, propensity score
- **Email Preview**: Complete formatted email content
- **Agent Information**: Assigned agent and contact details
- **Approval Actions**: Approve or reject email

### Visual Features
- **Color Coding**: Propensity scores and status indicators
- **Professional Layout**: Business-appropriate design
- **Responsive Design**: Works on all devices
- **Loading States**: Progress indicators during operations

## Data Management

### Email Data Structure
```typescript
interface EmailDraft {
  customer_id: string;
  customer_name: string;
  product_name: string;
  subject: string;
  email_content: string;
  propensity_score: number;
  agent_name: string;
  agent_contact: string;
  generated_date: string;
  status: string;
}
```

### Agent Assignment
- **Sarah Johnson**: Senior Insurance Advisor
- **Michael Chen**: Insurance Protection Specialist
- **Emily Rodriguez**: Retirement Planning Specialist
- **David Kim**: Investment Insurance Specialist
- **Lisa Anderson**: Life Insurance Specialist

### Email Status Tracking
- **Draft**: Generated but not reviewed
- **Reviewed**: Previewed by user
- **Approved**: Ready to send
- **Rejected**: Email rejected
- **Sent**: Successfully delivered

## Technical Implementation

### Backend Features
- **Template Engine**: Dynamic email content generation
- **Personalization Logic**: Customer-specific content insertion
- **Error Handling**: Comprehensive error management
- **Data Validation**: Input validation and sanitization

### Frontend Features
- **State Management**: React hooks for email data
- **Navigation**: Seamless routing between pages
- **Dialog System**: Material UI dialog for email preview
- **Loading States**: Professional user feedback

### API Integration
- **Type Safety**: TypeScript interfaces for all data
- **Error Handling**: Consistent error management
- **Loading States**: Proper async operation handling
- **Data Caching**: Efficient data management

## Quality Assurance

### Email Content Quality
- **Professional Tone**: Business-appropriate language
- **Personalization**: Customer-specific details
- **Clear CTAs**: Actionable next steps
- **Compliance**: Regulatory compliance considerations

### User Experience Quality
- **Intuitive Navigation**: Clear user flow
- **Visual Feedback**: Loading and success states
- **Error Recovery**: Graceful error handling
- **Responsive Design**: Multi-device support

## Future Enhancements

### Advanced Features
- **A/B Testing**: Multiple email templates per product
- **Email Scheduling**: Send emails at optimal times
- **Analytics**: Email open and response tracking
- **CRM Integration**: Sync with customer management systems

### Automation Features
- **Smart Personalization**: AI-driven content optimization
- **Dynamic Templates**: Template performance optimization
- **Batch Processing**: Efficient bulk email generation
- **Quality Control**: Automated content review

### Integration Features
- **Email Service Integration**: Connect to email providers
- **Calendar Integration**: Schedule follow-up calls
- **Document Generation**: Create PDF proposals
- **Reporting**: Campaign performance analytics

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

### Test Email Workflow
1. Start both servers
2. Upload sample files and run pipeline
3. Click on any product card
4. Click "Send Emails" button
5. Review generated emails in table
6. Click "Review Email" to preview
7. Approve or reject emails

## Technologies Used

### Frontend
- **React 19** - UI framework with hooks
- **TypeScript** - Type safety and interfaces
- **Material UI** - Professional component library
- **React Router** - Navigation and routing
- **Dialog System** - Email preview functionality

### Backend
- **FastAPI** - Python web framework
- **Template System** - Dynamic email generation
- **Data Management** - Customer and email data
- **Error Handling** - Comprehensive error management

The complete email outreach system provides a professional, scalable solution for personalized insurance marketing with review and approval workflows! 🎉
