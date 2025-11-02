#!/usr/bin/env python3
"""
Update products-simple.json with local image paths
Scans product_media directory and updates JSON with local image references
"""

import json
import os
from pathlib import Path

def get_local_images(media_dir: str, asin: str) -> list:
    """Get list of local image files for a product ASIN."""
    product_dir = Path(media_dir) / asin
    if not product_dir.exists():
        return []
    
    images = sorted([f for f in os.listdir(product_dir) if f.endswith('.jpg')])
    return [f"{media_dir}/{asin}/{img}" for img in images]

def get_local_videos(media_dir: str, asin: str) -> list:
    """Get list of local video files for a product ASIN."""
    product_dir = Path(media_dir) / asin
    if not product_dir.exists():
        return []
    
    videos = sorted([f for f in os.listdir(product_dir) if f.endswith('.mp4')])
    return [f"{media_dir}/{asin}/{vid}" for vid in videos]

def update_products_json(json_path: str, media_dir: str = "product_media"):
    """Update products JSON with local image and video paths."""
    
    # Load existing products
    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    stats = {
        'total_products': len(products),
        'products_with_images': 0,
        'products_with_videos': 0,
        'total_images': 0,
        'total_videos': 0,
        'updated_products': []
    }
    
    # Update each product
    for product in products:
        asin = product.get('asin')
        if not asin:
            continue
        
        # Get local images
        local_images = get_local_images(media_dir, asin)
        local_videos = get_local_videos(media_dir, asin)
        
        # Update product data
        if local_images:
            stats['products_with_images'] += 1
            stats['total_images'] += len(local_images)
            product['local_images'] = local_images
            # Update primary image_url to first local image if available
            product['image_url'] = local_images[0]
            product['image_count'] = len(local_images)
            stats['updated_products'].append(asin)
        
        if local_videos:
            stats['products_with_videos'] += 1
            stats['total_videos'] += len(local_videos)
            product['local_videos'] = local_videos
            product['video_count'] = len(local_videos)
    
    # Save updated JSON
    output_path = json_path.replace('.json', '-with-local-images.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    print("=" * 60)
    print("JSON Update Statistics")
    print("=" * 60)
    print(f"Total products: {stats['total_products']}")
    print(f"Products with local images: {stats['products_with_images']} ({stats['products_with_images']/stats['total_products']*100:.1f}%)")
    print(f"Products with local videos: {stats['products_with_videos']} ({stats['products_with_videos']/stats['total_products']*100:.1f}%)")
    print(f"Total images found: {stats['total_images']}")
    print(f"Total videos found: {stats['total_videos']}")
    print(f"Updated JSON saved to: {output_path}")
    print("=" * 60)
    
    return output_path, stats

if __name__ == "__main__":
    json_path = "products-simple.json"
    if os.path.exists(json_path):
        update_products_json(json_path)
    else:
        print(f"Error: {json_path} not found!")
