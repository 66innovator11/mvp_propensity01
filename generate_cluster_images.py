"""
Cluster Image Generator for Insurance Products
This script generates different cluster visualization images for each insurance product.
Run this script to create the cluster images that will be displayed in the UI.
"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_blobs
import os

# Create clusters directory if it doesn't exist
clusters_dir = "propensity-frontend/public/clusters"
os.makedirs(clusters_dir, exist_ok=True)

def generate_cluster_images():
    """Generate unique cluster visualizations for each insurance product"""
    
    # Define different cluster configurations for each product
    products = [
        {
            "name": "term_life_clusters",
            "title": "Term Life Insurance Clusters",
            "n_clusters": 4,
            "centers": [[2, 3], [8, 2], [5, 8], [9, 7]],
            "cluster_std": [0.8, 0.6, 0.7, 0.9],
            "colors": ['#4CAF50', '#FF9800', '#2196F3', '#9C27B0']
        },
        {
            "name": "critical_illness_clusters",
            "title": "Critical Illness Insurance Clusters",
            "n_clusters": 5,
            "centers": [[1, 1], [4, 7], [7, 3], [9, 8], [3, 5]],
            "cluster_std": [0.5, 0.7, 0.6, 0.8, 0.4],
            "colors": ['#F44336', '#FF9800', '#4CAF50', '#2196F3', '#9C27B0']
        },
        {
            "name": "annuity_clusters",
            "title": "Annuity Product Clusters",
            "n_clusters": 3,
            "centers": [[2, 5], [6, 2], [8, 8]],
            "cluster_std": [1.0, 0.8, 0.6],
            "colors": ['#FF5722', '#795548', '#607D8B']
        },
        {
            "name": "endowment_clusters",
            "title": "Endowment Insurance Clusters",
            "n_clusters": 4,
            "centers": [[1, 8], [4, 2], [7, 6], [9, 3]],
            "cluster_std": [0.6, 0.7, 0.5, 0.8],
            "colors": ['#E91E63', '#3F51B5', '#009688', '#FFC107']
        },
        {
            "name": "unit_linked_clusters",
            "title": "Unit Linked Insurance Clusters",
            "n_clusters": 6,
            "centers": [[1, 1], [2, 8], [4, 4], [6, 2], [8, 7], [9, 5]],
            "cluster_std": [0.4, 0.5, 0.6, 0.4, 0.7, 0.5],
            "colors": ['#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#FF9800', '#FF5722']
        },
        {
            "name": "whole_life_clusters",
            "title": "Whole Life Insurance Clusters",
            "n_clusters": 4,
            "centers": [[3, 3], [5, 7], [7, 2], [8, 8]],
            "cluster_std": [0.9, 0.6, 0.8, 0.5],
            "colors": ['#673AB7', '#2196F3', '#00BCD4', '#009688']
        }
    ]
    
    for product in products:
        # Generate synthetic data for clusters
        X, y = make_blobs(
            n_samples=300,
            centers=product["centers"],
            cluster_std=product["cluster_std"],
            random_state=42
        )
        
        # Create the plot
        plt.figure(figsize=(10, 8))
        
        # Plot each cluster with different color
        for i in range(product["n_clusters"]):
            cluster_points = X[y == i]
            plt.scatter(cluster_points[:, 0], cluster_points[:, 1], 
                       c=product["colors"][i], alpha=0.7, s=50,
                       label=f'Cluster {i+1}')
        
        # Customize the plot
        plt.title(product["title"], fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Customer Feature 1', fontsize=12)
        plt.ylabel('Customer Feature 2', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Set background color
        plt.gca().set_facecolor('#f8f9fa')
        plt.gcf().patch.set_facecolor('white')
        
        # Adjust layout and save
        plt.tight_layout()
        
        # Save the image
        filename = f"{product['name']}.jpg"
        filepath = os.path.join(clusters_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight', quality=95)
        plt.close()
        
        print(f"Generated: {filename}")
    
    print(f"\nAll cluster images generated in: {clusters_dir}")
    print("These images will be displayed dynamically in the UI for each insurance product.")

if __name__ == "__main__":
    print("Generating cluster visualization images for insurance products...")
    generate_cluster_images()
    print("Done! 🎉")
