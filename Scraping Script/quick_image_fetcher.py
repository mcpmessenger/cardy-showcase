"""
Quick script to fetch at least one image for each product by visiting Amazon pages.
This uses a simpler approach than the full scraper - just gets the main product image.
"""

import json
import os
import time
import requests
import re
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

def get_amazon_page_html(url: str) -> Optional[str]:
    """Fetch HTML from Amazon product page."""
    try:
        # Remove tag parameter as it might cause issues
        clean_url = url.split('?tag=')[0] if '?tag=' in url else url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        session = requests.Session()
        response = session.get(clean_url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"  Product page not found (404)")
        else:
            print(f"  HTTP Error: {e.response.status_code}")
        return None
    except Exception as e:
        print(f"  Error fetching page: {e}")
        return None

def extract_image_url_from_html(html: str, asin: str) -> Optional[str]:
    """Extract the main product image URL from Amazon HTML."""
    if not html:
        return None
    
    # More comprehensive patterns from the main scraper
    asin_pattern = re.escape(asin)
    image_urls = set()
    
    # Method 1: ASIN-specific patterns (most reliable)
    js_data_patterns = [
        # Pattern: "ASIN": { ... "colorImages": {...} ... }
        rf'"{asin_pattern}"\s*:\s*{{[^}}]*"colorImages"\s*:\s*{{[^}}]*"initial"\s*:\s*\[(.*?)\]',
        # Pattern: ColorToAsin mapping with image data
        rf'"colorToAsin"\s*:\s*{{[^}}]*"{asin_pattern}"\s*:\s*[^}}]*"colorImages"[^}}]*"initial"\s*:\s*\[(.*?)\]',
        # Pattern: imageBlockData containing ASIN
        rf'"imageBlockData"\s*:\s*\[[^\]]*"{asin_pattern}"[^\]]*\](.*?)"',
        # Landing image
        rf'"{asin_pattern}"[^}}]*"landingImageUrl"\s*:\s*"(https://[^"]+)"',
        # Main image URL
        rf'"{asin_pattern}"[^}}]*"mainImageUrl"\s*:\s*"(https://[^"]+)"',
        # Hi-res image
        rf'"{asin_pattern}"[^}}]*"hiResImage"\s*:\s*"(https://[^"]+)"',
    ]
    
    for pattern in js_data_patterns:
        matches = re.findall(pattern, html, re.DOTALL)
        for match in matches:
            if match.startswith('https://'):
                image_urls.add(match)
            else:
                # Extract URLs from JSON structure
                urls = re.findall(r'"url"\s*:\s*"([^"]+\.jpg[^"]*)"', match)
                clean_https = re.findall(r'(https://[^"]+\.jpg)', match)
                image_urls.update(urls + clean_https)
    
    # Method 2: Broader patterns if ASIN-specific didn't work
    if len(image_urls) == 0:
        broader_patterns = [
            r'"colorImages"\s*:\s*{\s*"initial"\s*:\s*\[(.*?)\]',
            r'"imageBlockData"[^]]*\[(.*?)\]',
            r'"mainImageUrl"\s*:\s*"(https://[^"]+\.jpg[^"]*)"',
            r'"hiResImage"\s*:\s*"(https://[^"]+\.jpg[^"]*)"',
            r'"landingImageUrl"\s*:\s*"(https://[^"]+\.jpg[^"]*)"',
            r'"(https://m\.media-amazon\.com/images/I/[^"]+\._AC_SL\d+_\.jpg)"',
        ]
        for pattern in broader_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                if isinstance(match, str):
                    if match.startswith('https://'):
                        image_urls.add(match)
                    else:
                        urls = re.findall(r'"url"\s*:\s*"([^"]+\.jpg[^"]*)"', match)
                        clean_https = re.findall(r'(https://[^"]+\.jpg)', match)
                        image_urls.update(urls + clean_https)
    
    # Clean and return first valid URL
    for url in image_urls:
        # Remove JSON artifacts
        url = re.sub(r'["\',\s}].*$', '', url)
        url = url.strip('"').strip()
        
        # Skip excluded patterns (related products, etc.)
        excluded = ['/related/', '/recommended/', '/sponsored/', '/customer/', '/review/']
        if any(excl in url for excl in excluded):
            continue
        
        # Must be valid Amazon media URL
        if url.startswith('https://m.media-amazon.com') and '.jpg' in url.lower() and len(url) > 30:
            return url
    
    return None

def download_image(url: str, output_path: str, timeout: int = 30) -> bool:
    """Download an image from URL to local path."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.amazon.com/'
        }
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Download image
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Verify file was downloaded and has content
        if os.path.getsize(output_path) < 1000:  # Less than 1KB is probably an error page
            os.remove(output_path)
            return False
        
        return True
    except Exception as e:
        print(f"    Error downloading: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

def main():
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
        url = product.get('url')
        local_images = product.get('local_images', [])
        
        if not asin or not url:
            continue
        
        # Check if product has local images
        has_local_images = len(local_images) > 0 and any(
            Path(output_dir / img_path.replace('product_media/', '')).exists() 
            for img_path in local_images 
            if 'product_media/' in img_path
        )
        
        # Also check if directory has image files
        product_dir = output_dir / asin
        has_image_files = product_dir.exists() and any(
            f.startswith('image_') and (f.endswith('.jpg') or f.endswith('.png'))
            for f in os.listdir(product_dir) if os.path.isfile(product_dir / f)
        )
        
        if not has_local_images and not has_image_files:
            products_needing_images.append({
                'asin': asin,
                'name': product.get('name', 'Unknown'),
                'url': url
            })
    
    print(f"Products needing images: {len(products_needing_images)}\n")
    
    if len(products_needing_images) == 0:
        print("All products already have images!")
        return
    
    # Process products
    success_count = 0
    fail_count = 0
    
    for idx, product in enumerate(products_needing_images, 1):
        asin = product['asin']
        name = product['name']
        url = product['url']
        
        print(f"[{idx}/{len(products_needing_images)}] Fetching image for {asin}: {name[:50]}...")
        
        # Create product directory
        product_dir = output_dir / asin
        product_dir.mkdir(exist_ok=True)
        
        # Skip if already has image
        existing_images = list(product_dir.glob('image_*.jpg')) + list(product_dir.glob('image_*.png'))
        if existing_images:
            print(f"  Image already exists, skipping...")
            success_count += 1
            continue
        
        # Fetch page HTML
        html = get_amazon_page_html(url)
        if not html:
            print(f"  [FAILED] Could not fetch page HTML")
            fail_count += 1
            time.sleep(2)  # Rate limiting
            continue
        
        # Extract image URL
        image_url = extract_image_url_from_html(html, asin)
        if not image_url:
            print(f"  [FAILED] Could not extract image URL from page")
            fail_count += 1
            time.sleep(2)
            continue
        
        print(f"  Found image URL, downloading...")
        
        # Download image
        output_path = product_dir / "image_01.jpg"
        if download_image(image_url, str(output_path)):
            # Copy to public folder
            import shutil
            public_product_dir = public_dir / asin
            public_product_dir.mkdir(parents=True, exist_ok=True)
            public_output_path = public_product_dir / "image_01.jpg"
            shutil.copy2(output_path, public_output_path)
            
            print(f"  [OK] Downloaded: {output_path.name}")
            success_count += 1
        else:
            print(f"  [FAILED] Could not download image")
            fail_count += 1
        
        # Rate limiting - be respectful to Amazon
        if idx < len(products_needing_images):
            time.sleep(3)  # 3 second delay between requests
    
    print(f"\n{'='*60}")
    print(f"Fetching complete!")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {fail_count}")
    print(f"  Total: {len(products_needing_images)}")
    print(f"\nImages saved to: {output_dir}")
    print(f"Copied to public folder: {public_dir}")
    print(f"\nNext step: Run update_json_with_local_images.py to update the JSON file.")

if __name__ == "__main__":
    main()

