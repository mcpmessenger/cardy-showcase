#!/usr/bin/env python3
"""
Amazon Product Image & Video Scraper (Selenium Version)
========================================================

This is an advanced version using Selenium WebDriver to handle JavaScript-rendered
content and dynamic image loading on Amazon product pages.

This approach is more robust but slower than the basic scraper. Use this if the
basic scraper is not finding all images.

Requirements:
    - selenium
    - webdriver-manager (automatically downloads ChromeDriver)
    - requests
    - beautifulsoup4
    - pillow

Installation:
    pip install selenium webdriver-manager requests beautifulsoup4 pillow
"""

import json
import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import requests
from urllib.parse import urljoin
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_selenium.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AmazonProductScraperSelenium:
    """
    Advanced Amazon product scraper using Selenium WebDriver.
    
    This scraper handles:
    - JavaScript-rendered images
    - Lazy-loaded images (scrolling to load more)
    - Dynamic image galleries
    - Video players
    - Cookie and consent management
    """
    
    def __init__(self, output_dir: str = "product_media", headless: bool = True):
        """
        Initialize the Selenium-based scraper.
        
        Args:
            output_dir: Base directory for saving media files
            headless: Run browser in headless mode (no GUI)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.headless = headless
        
        # Track downloaded files
        self.downloaded_hashes = set()
        
        # Session for downloading files
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.driver = None
    
    def init_driver(self):
        """Initialize Chrome WebDriver with optimized options."""
        chrome_options = webdriver.ChromeOptions()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Performance optimizations
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-web-resources')
        chrome_options.add_argument('--disable-extensions')
        
        # Avoid detection as bot
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            raise
    
    def close_driver(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("Chrome WebDriver closed")
    
    def load_product_page(self, url: str) -> bool:
        """
        Load a product page and wait for images to load.
        
        Args:
            url: Amazon product URL
            
        Returns:
            True if page loaded successfully
        """
        try:
            logger.info(f"Loading: {url}")
            self.driver.get(url)
            
            # Wait for main image to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "landingImage")))
            
            # Handle cookie consent if present
            try:
                consent_button = self.driver.find_element(By.ID, "sp-cc-accept")
                consent_button.click()
                logger.info("Accepted cookie consent")
                time.sleep(1)
            except NoSuchElementException:
                pass
            
            # Scroll to trigger lazy loading
            self.scroll_to_load_images()
            
            return True
        except TimeoutException:
            logger.warning(f"Timeout loading {url}")
            return False
        except Exception as e:
            logger.error(f"Error loading {url}: {e}")
            return False
    
    def scroll_to_load_images(self):
        """Scroll page to trigger lazy loading of images."""
        try:
            # Scroll to image gallery area
            image_gallery = self.driver.find_element(By.ID, "altImages")
            self.driver.execute_script("arguments[0].scrollIntoView();", image_gallery)
            time.sleep(2)
            
            # Scroll through thumbnails to load all images
            thumbnails = self.driver.find_elements(By.CLASS_NAME, "imageThumbnail")
            for idx, thumbnail in enumerate(thumbnails):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView();", thumbnail)
                    thumbnail.click()
                    time.sleep(0.5)
                except:
                    pass
            
            logger.info(f"Scrolled through {len(thumbnails)} image thumbnails")
        except Exception as e:
            logger.warning(f"Error scrolling for images: {e}")
    
    def extract_image_urls(self) -> List[str]:
        """
        Extract all image URLs from the loaded page.
        
        Returns:
            List of unique image URLs
        """
        image_urls = set()
        
        try:
            # Method 1: Get main image
            try:
                main_image = self.driver.find_element(By.ID, "landingImage")
                src = main_image.get_attribute("src")
                if src and '.jpg' in src.lower():
                    image_urls.add(src)
            except:
                pass
            
            # Method 2: Get all images from thumbnails
            try:
                thumbnails = self.driver.find_elements(By.CSS_SELECTOR, "img.imageThumbnail")
                for thumb in thumbnails:
                    src = thumb.get_attribute("src")
                    if src and '.jpg' in src.lower():
                        image_urls.add(src)
            except:
                pass
            
            # Method 3: Extract from page source (JavaScript variables)
            page_source = self.driver.page_source
            
            # Look for high-res images in JavaScript
            patterns = [
                r'"hiRes":"([^"]*\.jpg[^"]*)"',
                r'"imageUrl":"([^"]*\.jpg[^"]*)"',
                r'https://m\.media-amazon\.com/images/[^"]*\.jpg[^"]*',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_source)
                image_urls.update(matches)
            
            # Upgrade to high-resolution versions
            upgraded_urls = set()
            for url in image_urls:
                if '._AC_' in url:
                    # Upgrade resolution
                    upgraded = re.sub(r'_AC_SL\d+_', '_AC_SL1500_', url)
                    upgraded_urls.add(upgraded)
                else:
                    upgraded_urls.add(url)
            
            logger.info(f"Found {len(upgraded_urls)} unique image URLs")
            return list(upgraded_urls)
        
        except Exception as e:
            logger.error(f"Error extracting image URLs: {e}")
            return []
    
    def extract_video_urls(self) -> List[str]:
        """
        Extract video URLs from the page.
        
        Returns:
            List of video URLs
        """
        video_urls = set()
        
        try:
            page_source = self.driver.page_source
            
            # Look for video sources
            patterns = [
                r'<source[^>]*src="([^"]*\.mp4[^"]*)"',
                r'"videoUrl":"([^"]*\.mp4[^"]*)"',
                r'https://[^"]*\.mp4[^"]*',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_source)
                video_urls.update(matches)
            
            if video_urls:
                logger.info(f"Found {len(video_urls)} video URLs")
            
            return list(video_urls)
        
        except Exception as e:
            logger.error(f"Error extracting video URLs: {e}")
            return []
    
    def download_file(self, url: str, filename: str, max_retries: int = 3) -> bool:
        """
        Download a file from URL.
        
        Args:
            url: File URL
            filename: Path to save file
            max_retries: Number of retry attempts
            
        Returns:
            True if successful
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Downloading: {url}")
                response = self.session.get(url, timeout=15, stream=True)
                response.raise_for_status()
                
                file_size = int(response.headers.get('content-length', 0))
                if file_size == 0:
                    logger.warning(f"File size is 0 for {url}")
                    return False
                
                # Check for duplicates
                file_hash = hashlib.md5(response.content).hexdigest()
                if file_hash in self.downloaded_hashes:
                    logger.info(f"Duplicate file detected: {url}")
                    return False
                
                self.downloaded_hashes.add(file_hash)
                
                # Save file
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Saved: {filename} ({file_size / 1024 / 1024:.2f} MB)")
                return True
            
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        
        logger.error(f"Failed to download {url}")
        return False
    
    def process_product(self, product: Dict) -> Dict:
        """
        Process a single product.
        
        Args:
            product: Product dictionary
            
        Returns:
            Result dictionary
        """
        result = {
            'name': product.get('name', 'Unknown'),
            'asin': product.get('asin', 'Unknown'),
            'url': product.get('url', ''),
            'images_downloaded': 0,
            'videos_downloaded': 0,
            'errors': []
        }
        
        asin = product.get('asin')
        if not asin:
            result['errors'].append('No ASIN provided')
            return result
        
        product_dir = self.output_dir / asin
        product_dir.mkdir(exist_ok=True)
        
        # Load product page
        if not self.load_product_page(product.get('url', '')):
            result['errors'].append('Failed to load product page')
            return result
        
        # Extract and download images
        image_urls = self.extract_image_urls()
        for idx, img_url in enumerate(image_urls, 1):
            try:
                filename = product_dir / f"image_{idx:02d}.jpg"
                if self.download_file(img_url, str(filename)):
                    result['images_downloaded'] += 1
            except Exception as e:
                result['errors'].append(f"Image {idx} error: {str(e)}")
        
        # Extract and download videos
        video_urls = self.extract_video_urls()
        for idx, video_url in enumerate(video_urls, 1):
            try:
                ext = '.mp4' if '.mp4' in video_url.lower() else '.webm'
                filename = product_dir / f"video_{idx:02d}{ext}"
                if self.download_file(video_url, str(filename)):
                    result['videos_downloaded'] += 1
            except Exception as e:
                result['errors'].append(f"Video {idx} error: {str(e)}")
        
        # Save metadata
        metadata = {
            'name': product.get('name'),
            'asin': asin,
            'url': product.get('url'),
            'price': product.get('price'),
            'rating': product.get('rating'),
            'reviews': product.get('reviews'),
            'downloaded_at': datetime.now().isoformat(),
            'images_count': result['images_downloaded'],
            'videos_count': result['videos_downloaded']
        }
        
        metadata_file = product_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return result
    
    def scrape_products(self, products_file: str) -> List[Dict]:
        """
        Scrape all products from JSON file.
        
        Args:
            products_file: Path to products JSON file
            
        Returns:
            List of results
        """
        try:
            with open(products_file, 'r') as f:
                products = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load products file: {e}")
            return []
        
        self.init_driver()
        results = []
        
        try:
            for idx, product in enumerate(products, 1):
                logger.info(f"Processing {idx}/{len(products)}: {product.get('name')}")
                result = self.process_product(product)
                results.append(result)
                
                if result['images_downloaded'] > 0 or result['videos_downloaded'] > 0:
                    logger.info(f"  ✓ Downloaded {result['images_downloaded']} images, {result['videos_downloaded']} videos")
                if result['errors']:
                    for error in result['errors']:
                        logger.warning(f"  ⚠ {error}")
        
        finally:
            self.close_driver()
        
        return results
    
    def generate_report(self, results: List[Dict], output_file: str = "scrape_report_selenium.json"):
        """Generate a summary report."""
        total_images = sum(r['images_downloaded'] for r in results)
        total_videos = sum(r['videos_downloaded'] for r in results)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_products': len(results),
            'total_images_downloaded': total_images,
            'total_videos_downloaded': total_videos,
            'products': results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"SCRAPING COMPLETE (Selenium)")
        logger.info(f"{'='*60}")
        logger.info(f"Total products: {len(results)}")
        logger.info(f"Total images: {total_images}")
        logger.info(f"Total videos: {total_videos}")
        logger.info(f"Report: {output_file}")
        logger.info(f"{'='*60}\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Download product images and videos from Amazon (Selenium version)'
    )
    parser.add_argument('products_file', help='Path to products JSON file')
    parser.add_argument('--output-dir', default='product_media', help='Output directory')
    parser.add_argument('--report', default='scrape_report_selenium.json', help='Report file')
    parser.add_argument('--headless', action='store_true', default=True, help='Run in headless mode')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.products_file):
        logger.error(f"Products file not found: {args.products_file}")
        return
    
    scraper = AmazonProductScraperSelenium(output_dir=args.output_dir, headless=args.headless)
    results = scraper.scrape_products(args.products_file)
    scraper.generate_report(results, args.report)


if __name__ == '__main__':
    main()
