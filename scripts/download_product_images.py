"""
Quick script to download product images for specific ASINs.
Usage: python scripts/download_product_images.py B09BWFX1L6 B095CN96JS
"""

import json
import os
import sys
import time
import requests
import re
from pathlib import Path
from typing import List, Optional

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
        }
        session = requests.Session()
        response = session.get(clean_url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  Error fetching page: {e}")
        return None

def extract_image_urls_from_html(html: str, asin: str, max_images: int = 5) -> List[str]:
    """Extract main product image URLs from Amazon HTML."""
    if not html:
        return []
    
    image_urls = set()
    
    # Method 1: Try to find imageBlockData or colorImages JSON
    # Look for the large JavaScript data structure
    js_data_patterns = [
        # Pattern: imageBlockData array
        r'"imageBlockData"\s*:\s*\[(.*?)\]',
        # Pattern: colorImages with initial array
        r'"colorImages"\s*:\s*{\s*"initial"\s*:\s*\[(.*?)\]',
        # Pattern: mainImageData
        r'"mainImageData"\s*:\s*{(.*?)}',
        # Pattern: hiResImages
        r'"hiResImages"\s*:\s*\[(.*?)\]',
    ]
    
    for pattern in js_data_patterns:
        matches = re.findall(pattern, html, re.DOTALL)
        for match in matches:
            # Extract all URLs from JSON structure
            urls = re.findall(r'"url"\s*:\s*"([^"]+)"', match)
            urls.extend(re.findall(r'"(https://[^"]+\.jpg[^"]*)"', match))
            urls.extend(re.findall(r'"(https://m\.media-amazon\.com/images/[^"]+)"', match))
            image_urls.update(urls)
    
    # Method 2: Direct image URL patterns in HTML
    direct_patterns = [
        r'data-a-dynamic-image\s*=\s*"({[^}]+})"',
        r'id="landingImage"[^>]+data-a-dynamic-image\s*=\s*"({[^}]+})"',
        r'id="main-image"[^>]+src\s*=\s*"([^"]+\.jpg[^"]*)"',
        r'id="landingImage"[^>]+src\s*=\s*"([^"]+\.jpg[^"]*)"',
        r'data-old-src\s*=\s*"([^"]+\.jpg[^"]*)"',
        r'data-src\s*=\s*"([^"]+\.jpg[^"]*)"',
    ]
    
    for pattern in direct_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for match in matches:
            if isinstance(match, str):
                if match.startswith('{'):
                    # JSON object with multiple sizes
                    urls = re.findall(r'"(https://[^"]+\.jpg[^"]*)"', match)
                    image_urls.update(urls)
                elif match.startswith('https://'):
                    image_urls.add(match)
    
    # Method 3: Fallback - find any Amazon media image URLs
    if not image_urls:
        fallback_pattern = r'(https://m\.media-amazon\.com/images/I/[A-Za-z0-9_-]+\._AC_SL\d+_\.jpg)'
        matches = re.findall(fallback_pattern, html)
        image_urls.update(matches)
    
    # Clean and filter URLs
    clean_urls = []
    for url in image_urls:
        # Clean up URL
        url = re.sub(r'["\',\s}].*$', '', url)
        url = url.strip('"').strip("'").strip()
        
        # Skip invalid or non-product images
        if not url or len(url) < 30:
            continue
        if any(excl in url.lower() for excl in ['/related/', '/recommended/', '/sponsored/', '/customer/', '/review/', 'community-']):
            continue
        if not url.startswith('https://'):
            continue
        
        # Must be Amazon media URL
        if 'm.media-amazon.com' in url or 'images-amazon.com' in url:
            # Upgrade to high resolution if possible
            if '._AC_SL' in url:
                url = re.sub(r'_AC_SL\d+_', '_AC_SL1500_', url)
            elif '._AC_' not in url and '.jpg' in url.lower():
                # Try to add high-res suffix if missing
                url = url.replace('.jpg', '._AC_SL1500_.jpg')
            
            clean_urls.append(url)
    
    # Remove duplicates and return best quality images
    unique_urls = list(dict.fromkeys(clean_urls))
    
    # Sort by quality (SL1500 > SL1000 > SL750, etc.)
    def quality_score(url):
        if '_AC_SL1500_' in url: return 3
        if '_AC_SL1000_' in url: return 2
        if '_AC_SL750_' in url: return 1
        return 0
    
    unique_urls.sort(key=quality_score, reverse=True)
    return unique_urls[:max_images]

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
        
        # Verify file was downloaded
        if os.path.getsize(output_path) < 1000:
            os.remove(output_path)
            return False
        
        return True
    except Exception as e:
        print(f"    Error downloading: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

def download_images_for_asin(asin: str, name: str = None):
    """Download images for a specific ASIN."""
    print(f"\n{'='*60}")
    print(f"Processing: {asin}")
    if name:
        print(f"Product: {name[:80]}...")
    
    # Create directories
    project_root = Path(__file__).parent.parent
    public_dir = project_root / "public" / "product_media" / asin
    public_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if real images already exist (not placeholders)
    existing_images = list(public_dir.glob("image_*.jpg")) + list(public_dir.glob("image_*.png"))
    has_real_images = False
    if existing_images:
        # Check if images are real (larger than 100KB) or just placeholders
        for img_path in existing_images:
            if img_path.stat().st_size > 100000:  # Real images are usually > 100KB
                has_real_images = True
                break
        if has_real_images:
            print(f"  [OK] Real images already exist ({len(existing_images)} files)")
            return True
        else:
            print(f"  [INFO] Found placeholder images, downloading real images...")
            # Remove placeholder images
            for img_path in existing_images:
                try:
                    img_path.unlink()
                except:
                    pass
    
    # Construct Amazon URL
    amazon_url = f"https://www.amazon.com/dp/{asin}"
    print(f"  Fetching from: {amazon_url}")
    
    # Fetch page HTML
    html = get_amazon_page_html(amazon_url)
    if not html:
        print(f"  [FAILED] Failed to fetch page HTML")
        return False
    
    # Extract image URLs
    image_urls = extract_image_urls_from_html(html, asin, max_images=5)
    if not image_urls:
        print(f"  [FAILED] Could not extract image URLs from page")
        return False
    
    print(f"  Found {len(image_urls)} image URL(s)")
    
    # Download images
    downloaded_count = 0
    for img_idx, image_url in enumerate(image_urls, 1):
        output_path = public_dir / f"image_{img_idx:02d}.jpg"
        print(f"  Downloading image {img_idx}...")
        if download_image(image_url, str(output_path)):
            print(f"    [OK] Saved: {output_path.name}")
            downloaded_count += 1
        else:
            print(f"    [FAILED] Failed to download image {img_idx}")
    
    if downloaded_count > 0:
        print(f"  [OK] Successfully downloaded {downloaded_count} image(s)")
        return True
    else:
        print(f"  [FAILED] Failed to download any images")
        return False

def main():
    # Default ASINs if none provided
    if len(sys.argv) > 1:
        asins = sys.argv[1:]
    else:
        # Default to the two new products
        asins = ["B09BWFX1L6", "B095CN96JS"]
    
    print(f"Downloading images for {len(asins)} product(s)...")
    
    # Load product names from JSON
    project_root = Path(__file__).parent.parent
    json_file = project_root / "products-simple.json"
    
    product_names = {}
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
                for product in products:
                    asin = product.get('asin')
                    if asin:
                        product_names[asin] = product.get('name', '')
        except:
            pass
    
    # Download images for each ASIN
    success_count = 0
    for asin in asins:
        name = product_names.get(asin)
        if download_images_for_asin(asin, name):
            success_count += 1
        time.sleep(2)  # Rate limiting
    
    print(f"\n{'='*60}")
    print(f"Download complete!")
    print(f"  Successful: {success_count}/{len(asins)}")
    print(f"\nImages saved to: public/product_media/")

if __name__ == "__main__":
    main()

