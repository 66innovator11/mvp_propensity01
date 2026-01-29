"""
Script to run the FastAPI server for propensity analysis.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

if __name__ == "__main__":
    # Change to src directory
    os.chdir(src_dir)
    
    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(src_dir)],
        log_level="info"
    )
