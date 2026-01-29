"""
FastAPI application for propensity analysis operations.

This module provides REST API endpoints for all propensity analysis operations
that can be invoked from a UI.
"""

import asyncio
import os
import tempfile
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd

from propensity.clustering.run_customer_clustering import main as run_clustering
from propensity.analysis.train_propensity_models import main as train_models
from propensity.analysis.auto_explain import main as auto_explain
from propensity.analysis.summarize_propensity import main as summarize_propensity
from propensity.outreach.generate_personalized_outreach import main as generate_outreach
from propensity.utils.paths import get_resource_path, get_output_path


# Pydantic models for API requests/responses
class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: Optional[float] = None
    message: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ClusteringRequest(BaseModel):
    k_min: int = 2
    k_max: int = 10
    random_state: int = 42


class TrainingRequest(BaseModel):
    random_state: int = 42


class OutreachRequest(BaseModel):
    sample_size: int = 10
    use_llm: bool = False
    model: str = "gpt-3.5-turbo"


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None


# Initialize FastAPI app
app = FastAPI(
    title="Propensity Analysis API",
    description="API for customer propensity analysis, clustering, and personalized outreach generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global job tracking
jobs: Dict[str, JobStatus] = {}


def create_job(job_id: str, status: str = "pending", message: str = None) -> JobStatus:
    """Create a new job status."""
    now = datetime.now()
    job = JobStatus(
        job_id=job_id,
        status=status,
        message=message,
        created_at=now,
        updated_at=now
    )
    jobs[job_id] = job
    return job


def update_job(job_id: str, status: str = None, progress: float = None, 
               message: str = None, result: Dict = None, error: str = None):
    """Update job status."""
    if job_id in jobs:
        job = jobs[job_id]
        if status:
            job.status = status
        if progress is not None:
            job.progress = progress
        if message:
            job.message = message
        if result:
            job.result = result
        if error:
            job.error = error
        job.updated_at = datetime.now()


async def run_job_async(job_id: str, func, *args, **kwargs):
    """Run a function asynchronously and update job status."""
    try:
        update_job(job_id, status="running", message="Starting job...")
        
        # Run the function
        result = func(*args, **kwargs)
        
        update_job(job_id, status="completed", progress=1.0, 
                  message="Job completed successfully", result={"exit_code": result})
    except Exception as e:
        update_job(job_id, status="failed", error=str(e), 
                  message=f"Job failed: {str(e)}")


@app.get("/", response_model=ApiResponse)
async def root():
    """Root endpoint."""
    return ApiResponse(success=True, message="Propensity Analysis API is running")


@app.get("/health", response_model=ApiResponse)
async def health_check():
    """Health check endpoint."""
    return ApiResponse(success=True, message="API is healthy")


@app.get("/jobs", response_model=List[JobStatus])
async def list_jobs():
    """List all jobs."""
    return list(jobs.values())


@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job(job_id: str):
    """Get job status by ID."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.post("/upload-data", response_model=ApiResponse)
async def upload_data(
    background_tasks: BackgroundTasks,
    customer_profile: UploadFile = File(...),
    insurance_products: UploadFile = File(...),
    transactions: UploadFile = File(...),
    customer_events: Optional[UploadFile] = File(None)
):
    """Upload CSV data files."""
    try:
        # Create temporary directory for uploads
        upload_dir = tempfile.mkdtemp(prefix="propensity_upload_")
        
        # Save uploaded files
        files = {
            "customer_profile.csv": customer_profile,
            "insurance_products.csv": insurance_products,
            "transactions.csv": transactions,
        }
        
        if customer_events:
            files["customer_events.csv"] = customer_events
        
        saved_files = {}
        for filename, file in files.items():
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            saved_files[filename] = file_path
        
        return ApiResponse(
            success=True,
            message="Data uploaded successfully",
            data={"upload_dir": upload_dir, "files": list(saved_files.keys())}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/clustering/start", response_model=ApiResponse)
async def start_clustering(
    background_tasks: BackgroundTasks,
    request: ClusteringRequest,
    data_dir: Optional[str] = None
):
    """Start customer clustering analysis."""
    job_id = str(uuid.uuid4())
    create_job(job_id, "pending", "Clustering job queued")
    
    # Use provided data_dir or default to resources
    if not data_dir:
        data_dir = get_resource_path("")
    
    # Set up sys.argv for clustering
    import sys
    original_argv = sys.argv.copy()
    
    async def run_clustering_job():
        sys.argv = [
            "run_clustering.py",
            "--data-dir", data_dir,
            "--output-dir", "outputs",
            "--k-min", str(request.k_min),
            "--k-max", str(request.k_max),
            "--random-state", str(request.random_state)
        ]
        await run_job_async(job_id, run_clustering)
        sys.argv = original_argv
    
    background_tasks.add_task(run_clustering_job)
    
    return ApiResponse(
        success=True,
        message="Clustering analysis started",
        data={"job_id": job_id}
    )


@app.post("/training/start", response_model=ApiResponse)
async def start_training(
    background_tasks: BackgroundTasks,
    request: TrainingRequest,
    data_dir: Optional[str] = None,
    outputs_dir: Optional[str] = None
):
    """Start propensity model training."""
    job_id = str(uuid.uuid4())
    create_job(job_id, "pending", "Model training job queued")
    
    if not data_dir:
        data_dir = get_resource_path("")
    if not outputs_dir:
        outputs_dir = "outputs"
    
    import sys
    original_argv = sys.argv.copy()
    
    async def run_training_job():
        sys.argv = [
            "train_propensity_models.py",
            "--data-dir", data_dir,
            "--outputs-dir", outputs_dir,
            "--propensity-dir", os.path.join(outputs_dir, "propensity_outputs"),
            "--random-state", str(request.random_state)
        ]
        await run_job_async(job_id, train_models)
        sys.argv = original_argv
    
    background_tasks.add_task(run_training_job)
    
    return ApiResponse(
        success=True,
        message="Model training started",
        data={"job_id": job_id}
    )


@app.post("/explain/start", response_model=ApiResponse)
async def start_explanation(
    background_tasks: BackgroundTasks,
    outputs_dir: Optional[str] = None
):
    """Start auto-explanation generation."""
    job_id = str(uuid.uuid4())
    create_job(job_id, "pending", "Auto-explanation job queued")
    
    if not outputs_dir:
        outputs_dir = "outputs"
    
    import sys
    original_argv = sys.argv.copy()
    
    async def run_explain_job():
        sys.argv = [
            "auto_explain.py",
            "--outputs-dir", outputs_dir
        ]
        await run_job_async(job_id, auto_explain)
        sys.argv = original_argv
    
    background_tasks.add_task(run_explain_job)
    
    return ApiResponse(
        success=True,
        message="Auto-explanation started",
        data={"job_id": job_id}
    )


@app.post("/summarize/start", response_model=ApiResponse)
async def start_summarization(
    background_tasks: BackgroundTasks,
    outputs_dir: Optional[str] = None
):
    """Start propensity summarization."""
    job_id = str(uuid.uuid4())
    create_job(job_id, "pending", "Summarization job queued")
    
    if not outputs_dir:
        outputs_dir = "outputs"
    
    import sys
    original_argv = sys.argv.copy()
    
    async def run_summarize_job():
        sys.argv = [
            "summarize_propensity.py",
            "--propensity-dir", os.path.join(outputs_dir, "propensity_outputs")
        ]
        await run_job_async(job_id, summarize_propensity)
        sys.argv = original_argv
    
    background_tasks.add_task(run_summarize_job)
    
    return ApiResponse(
        success=True,
        message="Summarization started",
        data={"job_id": job_id}
    )


@app.post("/outreach/start", response_model=ApiResponse)
async def start_outreach(
    background_tasks: BackgroundTasks,
    request: OutreachRequest,
    data_dir: Optional[str] = None,
    outputs_dir: Optional[str] = None
):
    """Start personalized outreach generation."""
    job_id = str(uuid.uuid4())
    create_job(job_id, "pending", "Outreach generation job queued")
    
    if not data_dir:
        data_dir = get_resource_path("")
    if not outputs_dir:
        outputs_dir = "outputs"
    
    import sys
    original_argv = sys.argv.copy()
    
    async def run_outreach_job():
        sys.argv = [
            "generate_personalized_outreach.py",
            "--data-dir", data_dir,
            "--propensity-dir", os.path.join(outputs_dir, "propensity_outputs"),
            "--outputs-dir", os.path.join(outputs_dir, "outreach_outputs"),
            "--sample-size", str(request.sample_size),
            "--use-llm", str(request.use_llm).lower(),
            "--model", request.model
        ]
        await run_job_async(job_id, generate_outreach)
        sys.argv = original_argv
    
    background_tasks.add_task(run_outreach_job)
    
    return ApiResponse(
        success=True,
        message="Outreach generation started",
        data={"job_id": job_id}
    )


@app.post("/pipeline/start", response_model=ApiResponse)
async def start_full_pipeline(
    background_tasks: BackgroundTasks,
    clustering_request: ClusteringRequest = ClusteringRequest(),
    training_request: TrainingRequest = TrainingRequest(),
    outreach_request: OutreachRequest = OutreachRequest(),
    data_dir: Optional[str] = None
):
    """Start the complete propensity analysis pipeline."""
    job_id = str(uuid.uuid4())
    create_job(job_id, "pending", "Full pipeline job queued")
    
    if not data_dir:
        data_dir = get_resource_path("")
    
    async def run_pipeline_job():
        try:
            # Step 1: Clustering
            update_job(job_id, status="running", progress=0.1, message="Running clustering...")
            await run_job_async(f"{job_id}_clustering", run_clustering)
            
            # Step 2: Training
            update_job(job_id, progress=0.3, message="Training models...")
            await run_job_async(f"{job_id}_training", train_models)
            
            # Step 3: Auto-explanation
            update_job(job_id, progress=0.5, message="Generating explanations...")
            await run_job_async(f"{job_id}_explain", auto_explain)
            
            # Step 4: Summarization
            update_job(job_id, progress=0.7, message="Summarizing results...")
            await run_job_async(f"{job_id}_summarize", summarize_propensity)
            
            # Step 5: Outreach
            update_job(job_id, progress=0.9, message="Generating outreach...")
            await run_job_async(f"{job_id}_outreach", generate_outreach)
            
            update_job(job_id, status="completed", progress=1.0, 
                      message="Full pipeline completed successfully")
            
        except Exception as e:
            update_job(job_id, status="failed", error=str(e))
    
    background_tasks.add_task(run_pipeline_job)
    
    return ApiResponse(
        success=True,
        message="Full pipeline started",
        data={"job_id": job_id}
    )


@app.get("/results/clustering", response_model=ApiResponse)
async def get_clustering_results():
    """Get clustering analysis results."""
    try:
        outputs_dir = "outputs"
        results = {}
        
        # Load clustering metrics
        metrics_path = os.path.join(outputs_dir, "clustering_metrics.csv")
        if os.path.exists(metrics_path):
            results["metrics"] = pd.read_csv(metrics_path).to_dict("records")
        
        # Load cluster profiles
        profiles = {}
        profile_files = [
            "product_agnostic_cluster_profile.csv",
            "product_wise_cluster_profile_whole_life.csv",
            "product_wise_cluster_profile_term_life.csv"
        ]
        
        for profile_file in profile_files:
            profile_path = os.path.join(outputs_dir, profile_file)
            if os.path.exists(profile_path):
                profile_name = profile_file.replace(".csv", "").replace("_", " ")
                profiles[profile_name] = pd.read_csv(profile_path).to_dict("records")
        
        results["profiles"] = profiles
        
        return ApiResponse(
            success=True,
            message="Clustering results retrieved",
            data=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get clustering results: {str(e)}")


@app.get("/results/propensity", response_model=ApiResponse)
async def get_propensity_results():
    """Get propensity analysis results."""
    try:
        propensity_dir = os.path.join("outputs", "propensity_outputs")
        results = {}
        
        # Load combined propensity scores
        combined_path = os.path.join(propensity_dir, "propensity_combined.csv")
        if os.path.exists(combined_path):
            results["combined_scores"] = pd.read_csv(combined_path).to_dict("records")
        
        # Load propensity summary
        summary_path = os.path.join(propensity_dir, "propensity_summary_by_band.csv")
        if os.path.exists(summary_path):
            results["summary"] = pd.read_csv(summary_path).to_dict("records")
        
        # Load propensity with rationale
        rationale_path = os.path.join(propensity_dir, "propensity_summary_with_rationale.csv")
        if os.path.exists(rationale_path):
            results["rationale"] = pd.read_csv(rationale_path).to_dict("records")
        
        return ApiResponse(
            success=True,
            message="Propensity results retrieved",
            data=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get propensity results: {str(e)}")


@app.get("/results/outreach", response_model=ApiResponse)
async def get_outreach_results():
    """Get outreach generation results."""
    try:
        outreach_dir = os.path.join("outputs", "outreach_outputs")
        results = {}
        
        # List all outreach files
        if os.path.exists(outreach_dir):
            outreach_files = [f for f in os.listdir(outreach_dir) if f.endswith('.csv')]
            for file in outreach_files:
                file_path = os.path.join(outreach_dir, file)
                file_name = file.replace('.csv', '')
                results[file_name] = pd.read_csv(file_path).to_dict("records")
        
        return ApiResponse(
            success=True,
            message="Outreach results retrieved",
            data=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get outreach results: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
