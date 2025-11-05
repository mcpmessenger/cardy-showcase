"""
Simple Selenium scraper for downloading Amazon product images.
This version avoids webdriver-manager issues by using a simpler approach.
"""

import json
import os
import time
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def download_image(url: str, output_path: str) -> bool:
    """Download an image from URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.amazon.com/'
        }
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        if os.path.getsize(output_path) < 1000:
            os.remove(output_path)
            return False
        
        return True
    except Exception as e:
        print(f"    Error downloading: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

def scrape_product_images(asin: str, name: str, url: str, output_dir: Path):
    """Scrape images for a single product."""
    print(f"\n{'='*60}")
    print(f"Processing: {asin}")
    print(f"Product: {name[:80]}...")
    
    product_dir = output_dir / asin
    product_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if real images already exist
    existing = list(product_dir.glob("image_*.jpg"))
    if existing and any(f.stat().st_size > 100000 for f in existing):
        print(f"  [OK] Real images already exist")
        return True
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # Try to find ChromeDriver in common locations or use system PATH
    driver = None
    try:
        # Try without explicit service first (uses system PATH)
        driver = webdriver.Chrome(options=chrome_options)
        print("  Chrome WebDriver initialized")
    except Exception as e:
        print(f"  [ERROR] Failed to initialize Chrome: {e}")
        print("  Make sure ChromeDriver is in your PATH or install it manually")
        return False
    
    try:
        print(f"  Loading: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Try to accept cookies
        try:
            consent = driver.find_element(By.ID, "sp-cc-accept")
            consent.click()
            time.sleep(1)
        except:
            pass
        
        # Get main image
        image_urls = set()
        
        # Method 1: Get landing image
        try:
            main_img = driver.find_element(By.ID, "landingImage")
            src = main_img.get_attribute("src")
            if src and 'media-amazon.com' in src:
                # Upgrade to high-res
                if '._AC_SL' in src:
                    src = src.replace('._AC_SL150_', '._AC_SL1500_')
                    src = src.replace('._AC_SL300_', '._AC_SL1500_')
                    src = src.replace('._AC_SL500_', '._AC_SL1500_')
                    src = src.replace('._AC_SL750_', '._AC_SL1500_')
                    src = src.replace('._AC_SL1000_', '._AC_SL1500_')
                image_urls.add(src)
                print(f"  Found main image")
        except Exception as e:
            print(f"  Could not find main image: {e}")
        
        # Method 2: Get thumbnails
        try:
            thumbnails = driver.find_elements(By.CSS_SELECTOR, "img.imageThumbnail, ul.altImages img")
            for thumb in thumbnails[:5]:  # Limit to 5 images
                try:
                    src = thumb.get_attribute("src") or thumb.get_attribute("data-src")
                    if src and 'media-amazon.com' in src and '.jpg' in src.lower():
                        if '._AC_SL' in src:
                            src = src.replace('._AC_SL150_', '._AC_SL1500_')
                            src = src.replace('._AC_SL300_', '._AC_SL500_')
                            src = src.replace('._AC_SL500_', '._AC_SL1500_')
                            src = src.replace('._AC_SL750_', '._AC_SL1500_')
                            src = src.replace('._AC_SL1000_', '._AC_SL1500_')
                        image_urls.add(src)
                except:
                    pass
            if thumbnails:
                print(f"  Found {len(thumbnails)} thumbnail(s)")
        except:
            pass
        
        # Download images
        if not image_urls:
            print(f"  [FAILED] No images found")
            return False
        
        print(f"  Found {len(image_urls)} unique image URL(s)")
        
        downloaded = 0
        for idx, img_url in enumerate(list(image_urls)[:5], 1):
            output_path = product_dir / f"image_{idx:02d}.jpg"
            print(f"  Downloading image {idx}...")
            if download_image(img_url, str(output_path)):
                print(f"    [OK] Saved: {output_path.name}")
                downloaded += 1
            else:
                print(f"    [FAILED] Could not download")
        
        if downloaded > 0:
            print(f"  [OK] Successfully downloaded {downloaded} image(s)")
            return True
        else:
            print(f"  [FAILED] Could not download any images")
            return False
            
    finally:
        driver.quit()
        print("  Chrome WebDriver closed")

def main():
    import sys
    
    # Load products
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = "temp_scrape_products.json"
    
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        return
    
    with open(json_file, 'r') as f:
        products = json.load(f)
    
    # Process all products in the JSON file
    
    print(f"Scraping {len(products)} product(s)...")
    
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "public" / "product_media"
    
    success = 0
    for product in products:
        asin = product.get('asin')
        name = product.get('name', '')
        url = product.get('url', f"https://www.amazon.com/dp/{asin}")
        
        if scrape_product_images(asin, name, url, output_dir):
            success += 1
        time.sleep(2)  # Rate limiting
    
    print(f"\n{'='*60}")
    print(f"Complete! Successfully scraped: {success}/{len(products)}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()

