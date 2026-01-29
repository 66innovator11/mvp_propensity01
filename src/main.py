"""
Main entry point for the propensity analysis package.

This script provides a unified interface to run the complete propensity analysis pipeline.
"""

import argparse
import os
import sys

from propensity.clustering.run_customer_clustering import main as run_clustering
from propensity.analysis.train_propensity_models import main as train_models
from propensity.analysis.auto_explain import main as auto_explain
from propensity.analysis.summarize_propensity import main as summarize_propensity
from propensity.outreach.generate_personalized_outreach import main as generate_outreach
from propensity.utils.paths import get_resource_path


def main():
    parser = argparse.ArgumentParser(description="Propensity Analysis Pipeline")
    parser.add_argument(
        "--step", 
        choices=["clustering", "training", "explain", "summarize", "outreach", "all"],
        default="all",
        help="Which step to run (default: all)"
    )
    parser.add_argument(
        "--data-dir", 
        default=get_resource_path(""),
        help="Directory containing input CSV files"
    )
    parser.add_argument(
        "--outputs-dir", 
        default="outputs",
        help="Directory for output files"
    )
    parser.add_argument(
        "--random-state", 
        type=int, 
        default=42,
        help="Random state for reproducibility"
    )
    
    args = parser.parse_args()
    
    # Ensure data directory exists
    if not os.path.exists(args.data_dir):
        print(f"Error: Data directory {args.data_dir} does not exist")
        return 1
    
    # Create outputs directory
    os.makedirs(args.outputs_dir, exist_ok=True)
    
    # Set up sys.argv for sub-modules
    original_argv = sys.argv.copy()
    
    try:
        if args.step in ["clustering", "all"]:
            print("Running customer clustering...")
            sys.argv = [
                "run_clustering.py",
                "--data-dir", args.data_dir,
                "--output-dir", args.outputs_dir,
                "--random-state", str(args.random_state)
            ]
            result = run_clustering()
            if result != 0:
                print(f"Clustering failed with exit code {result}")
                return result
        
        if args.step in ["training", "all"]:
            print("Training propensity models...")
            sys.argv = [
                "train_propensity_models.py",
                "--data-dir", args.data_dir,
                "--outputs-dir", args.outputs_dir,
                "--propensity-dir", os.path.join(args.outputs_dir, "propensity_outputs"),
                "--random-state", str(args.random_state)
            ]
            result = train_models()
            if result != 0:
                print(f"Model training failed with exit code {result}")
                return result
        
        if args.step in ["explain", "all"]:
            print("Generating auto-explanations...")
            sys.argv = [
                "auto_explain.py",
                "--outputs-dir", args.outputs_dir
            ]
            result = auto_explain()
            if result != 0:
                print(f"Auto-explanation failed with exit code {result}")
                return result
        
        if args.step in ["summarize", "all"]:
            print("Summarizing propensity results...")
            sys.argv = [
                "summarize_propensity.py",
                "--propensity-dir", os.path.join(args.outputs_dir, "propensity_outputs")
            ]
            result = summarize_propensity()
            if result != 0:
                print(f"Summarization failed with exit code {result}")
                return result
        
        if args.step in ["outreach", "all"]:
            print("Generating personalized outreach...")
            sys.argv = [
                "generate_personalized_outreach.py",
                "--data-dir", args.data_dir,
                "--propensity-dir", os.path.join(args.outputs_dir, "propensity_outputs"),
                "--outputs-dir", os.path.join(args.outputs_dir, "outreach_outputs")
            ]
            result = generate_outreach()
            if result != 0:
                print(f"Outreach generation failed with exit code {result}")
                return result
        
        print("Pipeline completed successfully!")
        return 0
        
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    sys.exit(main())
