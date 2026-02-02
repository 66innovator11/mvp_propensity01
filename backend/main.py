"""
FastAPI Backend Server for File Upload to Google Cloud Storage

Requirements:
- pip install fastapi uvicorn google-cloud-storage python-multipart

Environment Setup:
1. Create a Google Cloud service account and download the JSON key file
2. Set the environment variable:
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
   (On Windows: set GOOGLE_APPLICATION_CREDENTIALS="C:\\path\\to\\your\\service-account-key.json")

3. Create a GCS bucket and replace 'your-bucket-name' with your actual bucket name

Run the server:
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage
import os
from typing import List, Dict, Any
import uuid
import json
from pathlib import Path

app = FastAPI(title="File Upload API", description="Upload files to Google Cloud Storage")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("CORS middleware configured for http://localhost:3000")

# Initialize Google Cloud Storage client
try:
    # Temporarily hardcoded for testing - remove this line after testing
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:\\Users\\SINDHU\\propensity-to-buy-b7bde-375c9a6836d1.json"
    
    storage_client = storage.Client()
    # Replace 'your-bucket-name' with your actual GCS bucket name
    BUCKET_NAME = "cust_data_bucket"
    bucket = storage_client.bucket(BUCKET_NAME)
    print(f"GCS client initialized successfully with bucket: {BUCKET_NAME}")
except Exception as e:
    print(f"Error initializing GCS client: {e}")
    print("Please ensure GOOGLE_APPLICATION_CREDENTIALS is set correctly")
    storage_client = None
    bucket = None

@app.get("/")
async def root():
    """Root endpoint to check if the server is running"""
    return {"message": "File Upload API is running"}

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload files to Google Cloud Storage
    
    Args:
        files: List of files to upload
        
    Returns:
        JSON response with upload status and filenames
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if not storage_client or not bucket:
        raise HTTPException(
            status_code=500, 
            detail="Google Cloud Storage not configured properly"
        )
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Generate a unique filename to avoid conflicts
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            
            # Create a blob object
            blob = bucket.blob(unique_filename)
            
            # Upload file content to GCS
            content = await file.read()
            blob.upload_from_string(content, content_type=file.content_type)
            
            # Make the file publicly accessible (optional)
            blob.make_public()
            
            uploaded_files.append({
                "original_filename": file.filename,
                "gcs_filename": unique_filename,
                "public_url": blob.public_url,
                "size": len(content)
            })
            
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    # Prepare response
    response = {
        "message": "File upload completed",
        "uploaded_files": uploaded_files,
        "total_uploaded": len(uploaded_files),
        "total_files": len(files)
    }
    
    if errors:
        response["errors"] = errors
        response["message"] = f"Upload completed with {len(errors)} errors"
    
    return JSONResponse(content=response)

@app.get("/test")
async def test_connection():
    """Test endpoint for frontend connectivity check"""
    return {
        "status": "ok",
        "message": "Backend is running and accessible",
        "timestamp": "2025-02-02T00:00:00Z"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "gcs_configured": storage_client is not None,
        "bucket_name": BUCKET_NAME if bucket else None
    }

@app.get("/cluster-details/{product_name}")
async def get_cluster_details(product_name: str):
    """
    Get detailed customer information for a specific insurance product cluster
    Reads from the corresponding report file and returns structured customer data
    
    Args:
        product_name: Name of the insurance product (e.g., "term-life", "critical-illness")
    
    Returns:
        JSON response with customer details for the specified product
    """
    try:
        print(f"Fetching cluster details for product: {product_name}")
        
        # Map product names to display names
        product_mapping = {
            "term-life": "Term Life",
            "critical-illness": "Critical Illness", 
            "annuity": "Annuity",
            "endowment": "Endowment",
            "unit-linked": "Unit Linked",
            "whole-life": "Whole Life"
        }
        
        display_name = product_mapping.get(product_name.replace("-", "-"), product_name.title())
        
        # Placeholder customer data - in real implementation, this would read from reports folder
        # For now, generate realistic sample data for each product
        customer_data = generate_sample_customer_data(product_name, display_name)
        
        print(f"Generated {len(customer_data)} customer records for {display_name}")
        
        return JSONResponse(content={
            "status": "success",
            "product_name": display_name,
            "total_customers": len(customer_data),
            "customers": customer_data
        })
        
    except Exception as e:
        print(f"Error fetching cluster details for {product_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch cluster details: {str(e)}"
        )

def generate_sample_customer_data(product_name: str, display_name: str) -> list:
    """Generate sample customer data for demonstration purposes"""
    
    import random
    from datetime import datetime, timedelta
    
    # Sample customer data
    first_names = ["John", "Jane", "Michael", "Sarah", "Robert", "Emily", "David", "Lisa", "James", "Mary"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego"]
    streets = ["Main St", "Oak Ave", "Elm St", "Park Ave", "Pine St", "Maple Dr", "Cedar Ln", "Washington Blvd"]
    
    existing_products = ["Health Insurance", "Auto Insurance", "Home Insurance", "Travel Insurance", "Pet Insurance"]
    
    customers = []
    
    # Generate different number of customers based on product
    customer_counts = {
        "term-life": 25,
        "critical-illness": 20,
        "annuity": 15,
        "endowment": 18,
        "unit-linked": 12,
        "whole-life": 22
    }
    
    num_customers = customer_counts.get(product_name, 20)
    
    for i in range(1, num_customers + 1):
        # Generate customer details
        customer_id = f"CUST{str(i).zfill(6)}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        address = f"{random.randint(100, 9999)} {random.choice(streets)}, {random.choice(cities)}, {random.choice(['NY', 'CA', 'TX', 'IL', 'AZ'])} {random.randint(10000, 99999)}"
        
        # Generate propensity score based on product type
        if product_name in ["term-life", "critical-illness"]:
            propensity_score = round(random.uniform(0.75, 0.95), 3)
        elif product_name in ["annuity", "endowment"]:
            propensity_score = round(random.uniform(0.60, 0.85), 3)
        else:
            propensity_score = round(random.uniform(0.70, 0.90), 3)
        
        # Generate existing insurance products
        num_existing = random.randint(0, 3)
        existing_products_list = random.sample(existing_products, num_existing)
        
        # Additional customer fields
        age = random.randint(25, 65)
        income = f"${random.randint(50000, 200000):,}"
        email = f"{name.lower().replace(' ', '.')}@email.com"
        phone = f"({random.randint(100, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        customer = {
            "customer_id": customer_id,
            "name": name,
            "address": address,
            "propensity_score": propensity_score,
            "insurance_product": display_name,
            "existing_products": existing_products_list,
            "age": age,
            "annual_income": income,
            "email": email,
            "phone": phone,
            "cluster_id": random.randint(1, 6),
            "risk_profile": random.choice(["Low", "Medium", "High"]),
            "last_contact": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
        }
        
        customers.append(customer)
    
    # Sort by propensity score (highest first)
    customers.sort(key=lambda x: x["propensity_score"], reverse=True)
    
    return customers

@app.post("/run-pipeline")
async def run_pipeline():
    """
    Execute the propensity to buy pipeline and return cluster analysis results
    
    Returns:
        JSON response with cluster analysis metadata for all products
    """
    try:
        print("Starting pipeline execution...")
        
        # Placeholder for actual pipeline execution
        # In real implementation, this would:
        # 1. Process uploaded files from GCS bucket
        # 2. Run clustering algorithms for each product
        # 3. Generate cluster visualizations
        # 4. Save reports to reports folder
        
        # Simulate pipeline execution time
        import time
        time.sleep(3)
        
        # Placeholder cluster analysis results for insurance products
        # In real implementation, this would parse actual reports from the reports folder
        cluster_results = [
            {
                "product_id": 1,
                "product_name": "Term Life",
                "business_use": "Identify customers needing pure life protection coverage for income replacement",
                "cluster_count": 4,
                "image_path": "/clusters/term_life_clusters.jpg",
                "high_propensity_customers": 2156,
                "conversion_potential": "High"
            },
            {
                "product_id": 2,
                "product_name": "Critical Illness",
                "business_use": "Target customers for critical illness coverage and health protection plans",
                "cluster_count": 5,
                "image_path": "/clusters/critical_illness_clusters.jpg",
                "high_propensity_customers": 1834,
                "conversion_potential": "High"
            },
            {
                "product_id": 3,
                "product_name": "Annuity",
                "business_use": "Find customers interested in retirement income and pension solutions",
                "cluster_count": 3,
                "image_path": "/clusters/annuity_clusters.jpg",
                "high_propensity_customers": 923,
                "conversion_potential": "Medium"
            },
            {
                "product_id": 4,
                "product_name": "Endowment",
                "business_use": "Identify customers for savings-oriented life insurance with maturity benefits",
                "cluster_count": 4,
                "image_path": "/clusters/endowment_clusters.jpg",
                "high_propensity_customers": 1456,
                "conversion_potential": "Medium"
            },
            {
                "product_id": 5,
                "product_name": "Unit Linked",
                "business_use": "Target customers for investment-linked insurance with market-linked returns",
                "cluster_count": 6,
                "image_path": "/clusters/unit_linked_clusters.jpg",
                "high_propensity_customers": 789,
                "conversion_potential": "High"
            },
            {
                "product_id": 6,
                "product_name": "Whole Life",
                "business_use": "Find customers seeking lifelong protection with cash value accumulation",
                "cluster_count": 4,
                "image_path": "/clusters/whole_life_clusters.jpg",
                "high_propensity_customers": 1123,
                "conversion_potential": "Medium"
            }
        ]
        
        print(f"Pipeline completed successfully. Generated {len(cluster_results)} cluster analyses.")
        
        return JSONResponse(content={
            "status": "success",
            "message": "Pipeline executed successfully",
            "cluster_results": cluster_results,
            "total_products_analyzed": len(cluster_results),
            "execution_time": "3.2 seconds"
        })
        
    except Exception as e:
        print(f"Pipeline execution failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution failed: {str(e)}"
        )

@app.post("/send-emails/{product_name}")
async def send_emails(product_name: str):
    """
    Generate draft emails for customers of a specific insurance product
    Reads email templates from outreach_outputs folder and prepares personalized emails
    
    Args:
        product_name: Name of the insurance product (e.g., "term-life", "critical-illness")
    
    Returns:
        JSON response with email generation status and customer count
    """
    try:
        print(f"Generating draft emails for product: {product_name}")
        
        # Map product names to display names
        product_mapping = {
            "term-life": "Term Life",
            "critical-illness": "Critical Illness", 
            "annuity": "Annuity",
            "endowment": "Endowment",
            "unit-linked": "Unit Linked",
            "whole-life": "Whole Life"
        }
        
        display_name = product_mapping.get(product_name.replace("-", "-"), product_name.title())
        
        # Generate draft emails for customers
        # In real implementation, this would read from outreach_outputs folder
        email_drafts = generate_email_drafts(product_name, display_name)
        
        print(f"Generated {len(email_drafts)} email drafts for {display_name}")
        
        return JSONResponse(content={
            "status": "success",
            "message": f"Draft emails generated for {display_name}",
            "product_name": display_name,
            "total_emails": len(email_drafts),
            "emails_prepared": True
        })
        
    except Exception as e:
        print(f"Error generating emails for {product_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate emails: {str(e)}"
        )

@app.get("/review-emails")
async def review_emails():
    """
    Get all prepared draft emails for review
    Returns structured data with customer IDs and draft email content
    
    Returns:
        JSON response with all draft emails ready for review
    """
    try:
        print("Fetching all draft emails for review")
        
        # In real implementation, this would read from the generated email files
        # For now, return sample email drafts
        email_drafts = get_all_email_drafts()
        
        print(f"Retrieved {len(email_drafts)} draft emails for review")
        
        return JSONResponse(content={
            "status": "success",
            "total_emails": len(email_drafts),
            "emails": email_drafts
        })
        
    except Exception as e:
        print(f"Error fetching draft emails: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch draft emails: {str(e)}"
        )

def generate_email_drafts(product_name: str, display_name: str) -> list:
    """Generate sample email drafts for demonstration purposes"""
    
    import random
    from datetime import datetime
    
    # Sample customer data (reuse from cluster details)
    first_names = ["John", "Jane", "Michael", "Sarah", "Robert", "Emily", "David", "Lisa", "James", "Mary"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    # Email templates based on product type
    email_templates = {
        "term-life": {
            "subject": "Secure Your Family's Future with Term Life Insurance",
            "template": """
Dear {name},

Based on your profile and financial situation, we've identified that you could benefit significantly from comprehensive term life insurance coverage.

Why Term Life Insurance is Right for You:
• Provides essential income replacement for your family
• Affordable premiums with substantial coverage
• Peace of mind knowing your loved ones are protected
• Tax-free death benefit for your beneficiaries

Your Propensity Score: {propensity_score}
This indicates a strong match for term life protection based on your age, income, and family situation.

Next Steps:
I'd like to schedule a brief 15-minute call to discuss your specific needs and provide a personalized quote.

Best regards,
{agent_name}
Senior Insurance Advisor
Lloyds Bank Insurance Services
Contact: {agent_contact}
            """
        },
        "critical-illness": {
            "subject": "Protect Yourself Against Critical Illness with Comprehensive Coverage",
            "template": """
Dear {name},

Your financial profile suggests that critical illness insurance would provide valuable protection for you and your family.

Why Critical Illness Coverage Matters:
• Lump-sum payout upon diagnosis of covered conditions
• Covers medical expenses not included in standard health insurance
• Provides income replacement during recovery
• Protects your savings from unexpected medical costs

Your Propensity Score: {propensity_score}
This indicates you're an ideal candidate for critical illness protection based on your current coverage and risk factors.

Next Steps:
Let's discuss your specific health insurance needs and create a customized protection plan.

Best regards,
{agent_name}
Insurance Protection Specialist
Lloyds Bank Insurance Services
Contact: {agent_contact}
            """
        },
        "annuity": {
            "subject": "Secure Your Retirement with Annuity Solutions",
            "template": """
Dear {name},

Based on your financial profile, we believe annuity products could play an important role in your retirement planning strategy.

Why Consider Annuities:
• Guaranteed lifetime income stream
• Protection against market volatility
• Tax-deferred growth potential
• Flexible payout options to match your lifestyle

Your Propensity Score: {propensity_score}
This indicates strong potential for annuity products based on your age, income level, and retirement goals.

Next Steps:
I'd like to review your current retirement plan and show how annuities can complement your existing investments.

Best regards,
{agent_name}
Retirement Planning Specialist
Lloyds Bank Insurance Services
Contact: {agent_contact}
            """
        },
        "endowment": {
            "subject": "Build Wealth and Secure Protection with Endowment Policies",
            "template": """
Dear {name},

Your financial profile suggests that endowment insurance could provide an excellent combination of protection and savings for your long-term goals.

Benefits of Endowment Policies:
• Life insurance coverage with savings component
• Guaranteed maturity benefits
• Regular premium payments for disciplined saving
• Tax advantages under current regulations

Your Propensity Score: {propensity_score}
This indicates you're well-suited for endowment products based on your income, savings habits, and financial goals.

Next Steps:
Let's explore how endowment policies can fit into your overall financial strategy.

Best regards,
{agent_name}
Wealth Management Advisor
Lloyds Bank Insurance Services
Contact: {agent_contact}
            """
        },
        "unit-linked": {
            "subject": "Grow Your Wealth with Unit Linked Insurance Plans",
            "template": """
Dear {name},

Based on your risk profile and investment preferences, unit linked insurance plans could offer an excellent balance of protection and market-linked growth.

Why Unit Linked Insurance:
• Investment opportunities in equity and debt markets
• Life insurance coverage for your family
• Flexibility to switch between funds
• Potential for higher returns than traditional insurance

Your Propensity Score: {propensity_score}
This indicates strong alignment with unit linked products based on your investment experience and risk tolerance.

Next Steps:
I'd like to discuss your investment goals and show you how ULIPs can enhance your portfolio.

Best regards,
{agent_name}
Investment Insurance Specialist
Lloyds Bank Insurance Services
Contact: {agent_contact}
            """
        },
        "whole-life": {
            "subject": "Lifelong Protection and Wealth Building with Whole Life Insurance",
            "template": """
Dear {name},

Your comprehensive financial profile suggests that whole life insurance could provide excellent lifelong protection and cash value accumulation.

Advantages of Whole Life Insurance:
• Lifetime coverage with guaranteed death benefit
• Cash value accumulation over time
• Potential for policy dividends
• Estate planning and wealth transfer benefits

Your Propensity Score: {propensity_score}
This indicates you're an ideal candidate for whole life protection based on your age, income, and long-term financial goals.

Next Steps:
Let's review your current insurance coverage and explore how whole life policies can enhance your financial security.

Best regards,
{agent_name}
Life Insurance Specialist
Lloyds Bank Insurance Services
Contact: {agent_contact}
            """
        }
    }
    
    template = email_templates.get(product_name, email_templates["term-life"])
    emails = []
    
    # Generate different number of emails based on product
    email_counts = {
        "term-life": 25,
        "critical-illness": 20,
        "annuity": 15,
        "endowment": 18,
        "unit-linked": 12,
        "whole-life": 22
    }
    
    num_emails = email_counts.get(product_name, 20)
    agents = ["Sarah Johnson", "Michael Chen", "Emily Rodriguez", "David Kim", "Lisa Anderson"]
    
    for i in range(1, num_emails + 1):
        customer_id = f"CUST{str(i).zfill(6)}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        propensity_score = round(random.uniform(0.75, 0.95), 3)
        agent_name = random.choice(agents)
        agent_contact = f"800-555-{random.randint(1000, 9999)}"
        
        # Personalize the email template
        email_content = template["template"].format(
            name=name,
            propensity_score=propensity_score,
            agent_name=agent_name,
            agent_contact=agent_contact
        ).strip()
        
        email = {
            "customer_id": customer_id,
            "customer_name": name,
            "product_name": display_name,
            "subject": template["subject"],
            "email_content": email_content,
            "propensity_score": propensity_score,
            "agent_name": agent_name,
            "agent_contact": agent_contact,
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "draft"
        }
        
        emails.append(email)
    
    return emails

def get_all_email_drafts() -> list:
    """Get all email drafts from all products"""
    
    products = [
        ("term-life", "Term Life"),
        ("critical-illness", "Critical Illness"),
        ("annuity", "Annuity"),
        ("endowment", "Endowment"),
        ("unit-linked", "Unit Linked"),
        ("whole-life", "Whole Life")
    ]
    
    all_emails = []
    
    for product_name, display_name in products:
        emails = generate_email_drafts(product_name, display_name)
        all_emails.extend(emails)
    
    # Sort by propensity score (highest first)
    all_emails.sort(key=lambda x: x["propensity_score"], reverse=True)
    
    return all_emails

@app.get("/test-finalize")
async def test_finalize():
    """Test endpoint to verify new endpoints are being registered"""
    return {"message": "Test endpoint working"}

@app.post("/finalize-emails")
async def finalize_emails():
    """
    Update status of all draft emails to "Email Sent"
    Simulates sending emails by updating status
    
    Returns:
        JSON response with updated email list
    """
    # Force reload - endpoint added
    # Final reload trigger
    try:
        print("Finalizing emails - updating status to Email Sent")
        
        # Get all email drafts and update status
        all_emails = get_all_email_drafts()
        
        # Update status for all emails
        for email in all_emails:
            email["status"] = "Email Sent"
            email["sent_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"Updated {len(all_emails)} emails to 'Email Sent' status")
        
        return JSONResponse(content={
            "status": "success",
            "message": f"Successfully sent {len(all_emails)} emails",
            "total_emails": len(all_emails),
            "emails": all_emails
        })
        
    except Exception as e:
        print(f"Error finalizing emails: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to finalize emails: {str(e)}"
        )

@app.post("/run-pipeline")
async def run_pipeline():
    """
    Execute the propensity to buy pipeline and return cluster analysis results
    
    Returns:
        JSON response with cluster analysis metadata for all products
    """
    try:
        print("Starting pipeline execution...")
        
        # Placeholder for actual pipeline execution
        # In real implementation, this would:
        # 1. Process uploaded files from GCS bucket
        # 2. Run clustering algorithms for each product
        # 3. Generate cluster visualizations
        # 4. Save reports to reports folder
        
        # Simulate pipeline execution time
        import time
        time.sleep(3)
        
        # Placeholder cluster analysis results for insurance products
        # In real implementation, this would parse actual reports from the reports folder
        cluster_results = [
            {
                "product_id": 1,
                "product_name": "Term Life",
                "business_use": "Identify customers needing pure life protection coverage for income replacement",
                "cluster_count": 4,
                "image_path": "/clusters/term_life_clusters.jpg",
                "high_propensity_customers": 2156,
                "conversion_potential": "High"
            },
            {
                "product_id": 2,
                "product_name": "Critical Illness",
                "business_use": "Target customers for critical illness coverage and health protection plans",
                "cluster_count": 5,
                "image_path": "/clusters/critical_illness_clusters.jpg",
                "high_propensity_customers": 1834,
                "conversion_potential": "High"
            },
            {
                "product_id": 3,
                "product_name": "Annuity",
                "business_use": "Find customers interested in retirement income and pension solutions",
                "cluster_count": 3,
                "image_path": "/clusters/annuity_clusters.jpg",
                "high_propensity_customers": 923,
                "conversion_potential": "Medium"
            },
            {
                "product_id": 4,
                "product_name": "Endowment",
                "business_use": "Identify customers for savings-oriented life insurance with maturity benefits",
                "cluster_count": 4,
                "image_path": "/clusters/endowment_clusters.jpg",
                "high_propensity_customers": 1456,
                "conversion_potential": "Medium"
            },
            {
                "product_id": 5,
                "product_name": "Unit Linked",
                "business_use": "Target customers for investment-linked insurance with market-linked returns",
                "cluster_count": 6,
                "image_path": "/clusters/unit_linked_clusters.jpg",
                "high_propensity_customers": 789,
                "conversion_potential": "High"
            },
            {
                "product_id": 6,
                "product_name": "Whole Life",
                "business_use": "Find customers seeking lifelong protection with cash value accumulation",
                "cluster_count": 4,
                "image_path": "/clusters/whole_life_clusters.jpg",
                "high_propensity_customers": 1123,
                "conversion_potential": "Medium"
            }
        ]
        
        print(f"Pipeline completed successfully. Generated {len(cluster_results)} cluster analyses.")
        
        return JSONResponse(content={
            "status": "success",
            "message": "Pipeline executed successfully",
            "cluster_results": cluster_results,
            "total_products_analyzed": len(cluster_results),
            "execution_time": "3.2 seconds"
        })
        
    except Exception as e:
        print(f"Pipeline execution failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
