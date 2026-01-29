"""
Path utilities for the propensity package.
"""

import os
from typing import Optional


def get_resource_path(filename: str, resource_dir: Optional[str] = None) -> str:
    """
    Get the full path to a resource file.
    
    Args:
        filename: Name of the resource file
        resource_dir: Optional custom resource directory path
        
    Returns:
        Full path to the resource file
    """
    if resource_dir is None:
        # Default to the resources directory relative to the src folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.dirname(os.path.dirname(current_dir))
        resource_dir = os.path.join(src_dir, "resources")
    
    return os.path.join(resource_dir, filename)


def get_output_path(filename: str, output_dir: Optional[str] = None) -> str:
    """
    Get the full path to an output file.
    
    Args:
        filename: Name of the output file
        output_dir: Optional custom output directory path
        
    Returns:
        Full path to the output file
    """
    if output_dir is None:
        # Default to outputs directory in the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        output_dir = os.path.join(project_root, "outputs")
    
    return os.path.join(output_dir, filename)
