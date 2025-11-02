"""
Simple script to download at least one image for each product that doesn't have local images.
Uses the existing image_url from the JSON file and downloads it directly.
"""

import json
import os
import requests
from pathlib import Path
from typing import Dict, List
import time

def download_image(url: str, output_path: str, timeout: int = 30) -> bool:
    """Download an image from URL to local path."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Download image
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        return False

def get_image_extension(url: str) -> str:
    """Extract image extension from URL."""
    # Try to get extension from URL
    if '.jpg' in url.lower() or 'jpeg' in url.lower():
        return '.jpg'
    elif '.png' in url.lower():
        return '.png'
    elif '.webp' in url.lower():
        return '.webp'
    else:
        return '.jpg'  # Default to jpg

def check_product_has_images(product_dir: Path) -> bool:
    """Check if product directory has image files (not just metadata)."""
    if not product_dir.exists():
        return False
    
    image_files = list(product_dir.glob('image_*.jpg')) + \
                  list(product_dir.glob('image_*.png')) + \
                  list(product_dir.glob('image_*.webp'))
    
    return len(image_files) > 0

def main():
    # Paths
    script_dir = Path(__file__).parent
    json_file = script_dir / "products-simple.json"
    output_dir = script_dir / "product_media"
    public_dir = Path(script_dir.parent) / "public" / "product_media"
    
    # Create directories
    output_dir.mkdir(exist_ok=True)
    public_dir.mkdir(parents=True, exist_ok=True)
    
    # Load products
    print(f"Loading products from {json_file}...")
    with open(json_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"Found {len(products)} products\n")
    
    # Find products missing images
    products_needing_images = []
    for product in products:
        asin = product.get('asin')
        image_url = product.get('image_url')
        local_images = product.get('local_images', [])
        
        if not asin or not image_url:
            continue
        
        # Check if product has local images
        has_local_images = len(local_images) > 0 and any(
            Path(output_dir / img_path.replace('product_media/', '')).exists() 
            for img_path in local_images 
            if 'product_media/' in img_path
        )
        
        # Also check if directory has image files
        product_dir = output_dir / asin
        has_image_files = check_product_has_images(product_dir)
        
        if not has_local_images and not has_image_files:
            products_needing_images.append({
                'asin': asin,
                'name': product.get('name', 'Unknown'),
                'image_url': image_url
            })
    
    print(f"Products needing images: {len(products_needing_images)}\n")
    
    if len(products_needing_images) == 0:
        print("All products already have images!")
        return
    
    # Download images
    success_count = 0
    fail_count = 0
    
    for idx, product in enumerate(products_needing_images, 1):
        asin = product['asin']
        name = product['name']
        image_url = product['image_url']
        
        print(f"[{idx}/{len(products_needing_images)}] Downloading image for {asin}: {name[:60]}...")
        
        # Create product directory
        product_dir = output_dir / asin
        product_dir.mkdir(exist_ok=True)
        
        # Determine output path
        ext = get_image_extension(image_url)
        output_path = product_dir / f"image_01{ext}"
        
        # Skip if already exists
        if output_path.exists():
            print(f"  Image already exists, skipping...")
            success_count += 1
            continue
        
        # Download image
        if download_image(image_url, str(output_path)):
            # Copy to public folder for serving
            public_product_dir = public_dir / asin
            public_product_dir.mkdir(parents=True, exist_ok=True)
            
            import shutil
            public_output_path = public_product_dir / f"image_01{ext}"
            shutil.copy2(output_path, public_output_path)
            
            print(f"  [OK] Downloaded: {output_path.name}")
            success_count += 1
        else:
            print(f"  [FAILED] Failed to download")
            fail_count += 1
        
        # Rate limiting
        if idx < len(products_needing_images):
            time.sleep(1)  # 1 second delay between downloads
    
    print(f"\n{'='*60}")
    print(f"Download complete!")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {fail_count}")
    print(f"  Total: {len(products_needing_images)}")
    print(f"\nImages saved to: {output_dir}")
    print(f"Copied to public folder: {public_dir}")
    print(f"\nNext step: Run update_json_with_local_images.py to update the JSON file.")

if __name__ == "__main__":
    main()

