#!/usr/bin/env python3
"""
Image Audit Script
Identifies products with missing images, too many images, or image display issues.
"""

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PRODUCT_DATA_PATH = PROJECT_ROOT / "products-simple.json"
MEDIA_DIR = PROJECT_ROOT / "public" / "product_media"

def audit_images():
    """Audit all products for image issues."""
    print("=" * 80)
    print("PRODUCT IMAGE AUDIT REPORT")
    print("=" * 80)
    
    try:
        with open(PRODUCT_DATA_PATH, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print(f"Error: Product data file not found at {PRODUCT_DATA_PATH}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON: {e}")
        return

    total_products = len(products)
    
    # Categories of issues
    products_no_images = []
    products_missing_local_images = []
    products_too_many_images = []
    products_missing_image_url = []
    
    # Check each product
    for product in products:
        asin = product.get('asin', 'UNKNOWN')
        name = product.get('name', 'Unknown Product')[:60]
        local_images = product.get('local_images', [])
        image_url = product.get('image_url', '')
        image_count = len(local_images)
        
        # Issue 1: No images at all (no local_images AND no image_url)
        if not local_images and not image_url:
            products_no_images.append({
                'asin': asin,
                'name': name,
                'issue': 'NO_IMAGES'
            })
        
        # Issue 2: Has image_url but no local_images (should work but falls back)
        elif not local_images and image_url:
            products_missing_local_images.append({
                'asin': asin,
                'name': name,
                'image_url': image_url,
                'issue': 'NO_LOCAL_IMAGES'
            })
        
        # Issue 3: Too many images (over 20 can cause performance issues)
        elif image_count > 20:
            products_too_many_images.append({
                'asin': asin,
                'name': name,
                'count': image_count,
                'issue': 'TOO_MANY_IMAGES'
            })
        
        # Issue 4: Has local_images but no image_url fallback
        elif local_images and not image_url:
            products_missing_image_url.append({
                'asin': asin,
                'name': name,
                'local_count': image_count,
                'issue': 'NO_IMAGE_URL_FALLBACK'
            })
    
    # Print report
    print(f"\nTotal Products: {total_products}\n")
    
    # Critical issues
    print("-" * 80)
    print("CRITICAL ISSUES - Products with NO images at all")
    print("-" * 80)
    if products_no_images:
        print(f"Found {len(products_no_images)} products with NO images:")
        for p in products_no_images[:10]:
            print(f"  • [{p['asin']}] {p['name']}")
        if len(products_no_images) > 10:
            print(f"  ... and {len(products_no_images) - 10} more")
    else:
        print("[OK] No products without images found")
    
    # Warning: Too many images
    print("\n" + "-" * 80)
    print("PERFORMANCE WARNINGS - Products with 20+ images")
    print("-" * 80)
    if products_too_many_images:
        print(f"Found {len(products_too_many_images)} products with 20+ images (may cause display issues):")
        for p in sorted(products_too_many_images, key=lambda x: x['count'], reverse=True):
            print(f"  • [{p['asin']}] {p['name']} - {p['count']} images")
    else:
        print("[OK] No products with excessive images found")
    
    # Info: Missing local images
    print("\n" + "-" * 80)
    print("INFO - Products using Amazon CDN (no local images)")
    print("-" * 80)
    print(f"Found {len(products_missing_local_images)} products using image_url fallback:")
    if products_missing_local_images:
        print("  (These will display, but local images are preferred for better performance)")
        for p in products_missing_local_images[:5]:
            print(f"  • [{p['asin']}] {p['name']}")
        if len(products_missing_local_images) > 5:
            print(f"  ... and {len(products_missing_local_images) - 5} more")
    
    # Info: Missing image_url fallback
    print("\n" + "-" * 80)
    print("INFO - Products with local images but no image_url fallback")
    print("-" * 80)
    if products_missing_image_url:
        print(f"Found {len(products_missing_image_url)} products:")
        for p in products_missing_image_url[:5]:
            print(f"  • [{p['asin']}] {p['name']} - {p['local_count']} local images")
        if len(products_missing_image_url) > 5:
            print(f"  ... and {len(products_missing_image_url) - 5} more")
    else:
        print("[OK] All products with local images have image_url fallback")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Products with no images:           {len(products_no_images):3d}")
    print(f"Products with 20+ images:         {len(products_too_many_images):3d}")
    print(f"Products using image_url only:    {len(products_missing_local_images):3d}")
    print(f"Products missing image_url:       {len(products_missing_image_url):3d}")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if products_no_images:
        print("[CRITICAL] Fix products with no images:")
        print("  1. Add image_url from Amazon product page")
        print("  2. Or download images using scraping scripts")
    
    if products_too_many_images:
        print("[PERFORMANCE] Products with 20+ images are limited to first 20 in carousel")
        print("  This is handled automatically by ProductImageCarousel component")
        print("  Consider removing duplicate or low-quality images from local_images array")
    
    if products_missing_local_images:
        print("[OPTIMIZATION] Consider downloading local images for better performance:")
        print("  Run scraping scripts to download product images")
    
    print("\n" + "=" * 80)
    
    # Return data for potential fixes
    return {
        'no_images': products_no_images,
        'too_many_images': products_too_many_images,
        'missing_local': products_missing_local_images,
        'missing_url': products_missing_image_url
    }

if __name__ == "__main__":
    audit_images()

