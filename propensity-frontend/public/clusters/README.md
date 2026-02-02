# Cluster Images Folder

This folder contains cluster visualization images for each insurance product.

## Required Images:

Place your cluster graph images here with the following filenames:

1. **term_life_clusters.jpg** - Term Life Insurance cluster visualization
2. **critical_illness_clusters.jpg** - Critical Illness Insurance cluster visualization  
3. **annuity_clusters.jpg** - Annuity product cluster visualization
4. **endowment_clusters.jpg** - Endowment Insurance cluster visualization
5. **unit_linked_clusters.jpg** - Unit Linked Insurance cluster visualization
6. **whole_life_clusters.jpg** - Whole Life Insurance cluster visualization

## Image Specifications:
- **Format**: JPG or PNG
- **Recommended Size**: 800x600 pixels (or similar aspect ratio)
- **Content**: Cluster visualization showing customer segments with different colors
- **Quality**: Clear and readable cluster formations

## How It Works:
- The system will try to load each product's specific cluster image
- If an image is missing, it will automatically fall back to the default `cluster graph.jpg`
- Images are displayed dynamically based on the product

## Example:
If you have cluster graphs generated from your pipeline:
1. Save Term Life clusters as `term_life_clusters.jpg`
2. Save Critical Illness clusters as `critical_illness_clusters.jpg`
3. ... and so on for all products

The frontend will automatically display the correct cluster graph for each insurance product!
