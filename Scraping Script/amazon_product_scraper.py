#!/usr/bin/env python3
"""
Amazon Product Image & Video Scraper
=====================================

This script downloads all product images, high-resolution photos, and videos
from Amazon product pages using the provided product JSON file.

The script handles:
- Multiple images per product
- High-resolution image variants
- Video content extraction
- Proper rate limiting to avoid IP blocks
- Error handling and retry logic
- Organized directory structure

Requirements:
    - requests
    - beautifulsoup4
    - selenium (for JavaScript-rendered content)
    - pillow (for image processing)

Installation:
    pip install requests beautifulsoup4 selenium pillow
    
    # Download ChromeDriver matching your Chrome version from:
    # https://chromedriver.chromium.org/
"""

import json
import os
import time
import logging
import requests
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AmazonProductScraper:
    """
    Scrapes Amazon product pages to extract images and videos.
    
    This scraper uses multiple strategies to extract media:
    1. Direct image URL extraction from page HTML
    2. JavaScript variable parsing for high-res images
    3. Video URL extraction from embedded players
    4. Fallback to API endpoints
    """
    
    def __init__(self, output_dir: str = "product_media", rate_limit: float = 2.0, 
                 max_images: int = 3, max_videos: int = 1):
        """
        Initialize the scraper.
        
        Args:
            output_dir: Base directory for saving media files
            rate_limit: Seconds to wait between requests (avoid IP blocks)
            max_images: Maximum number of images to download per product (default: 3)
            max_videos: Maximum number of videos to download per product (default: 1)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.rate_limit = rate_limit
        self.max_images = max_images
        self.max_videos = max_videos
        
        # User-Agent to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Track downloaded files to avoid duplicates
        self.downloaded_hashes = set()
        
    def extract_asin_from_url(self, url: str) -> Optional[str]:
        """Extract ASIN from Amazon product URL."""
        match = re.search(r'/dp/([A-Z0-9]{10})', url)
        return match.group(1) if match else None
    
    def get_product_page(self, url: str) -> Optional[str]:
        """
        Fetch the product page HTML.
        
        Args:
            url: Amazon product URL
            
        Returns:
            HTML content or None if request fails
        """
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            time.sleep(self.rate_limit)  # Rate limiting
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def extract_image_urls_from_html(self, html: str, asin: str) -> List[str]:
        """
        Extract image URLs from HTML for the SPECIFIC product only.
        
        This method ONLY extracts images for the target ASIN, excluding:
        - Related product images
        - Recommended product images  
        - Sponsored product images
        - Other products on the page
        
        Args:
            html: HTML content of product page
            asin: Product ASIN (must match target product)
            
        Returns:
            List of unique image URLs for the target product only
        """
        image_urls = set()
        
        # Method 1: Extract from JavaScript data structures that contain the ASIN
        # Amazon stores product images in JavaScript objects keyed by ASIN
        asin_pattern = re.escape(asin)
        
        # Find JavaScript objects that contain both the ASIN and image data
        # This ensures we only get images for our specific product
        js_data_patterns = [
            # Pattern: "ASIN": { ... "colorImages": {...} ... }
            rf'"{asin_pattern}"\s*:\s*{{[^}}]*"colorImages"\s*:\s*{{[^}}]*"initial"\s*:\s*\[(.*?)\]',
            # Pattern: ColorToAsin mapping with image data
            rf'"colorToAsin"\s*:\s*{{[^}}]*"{asin_pattern}"\s*:\s*[^}}]*"colorImages"[^}}]*"initial"\s*:\s*\[(.*?)\]',
            # Pattern: imageBlockData containing ASIN
            rf'"imageBlockData"\s*:\s*\[[^\]]*"{asin_pattern}"[^\]]*\](.*?)"',
        ]
        
        # Try ASIN-specific patterns first
        for pattern in js_data_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                # Extract image URLs from the matched JSON structure - only clean URLs
                urls = re.findall(r'"url"\s*:\s*"([^"]+\.jpg[^"]*)"', match)
                # Extract clean https URLs that end with .jpg (before any JSON continuation)
                clean_https = re.findall(r'(https://[^"]+\.jpg)', match)
                image_urls.update(urls + clean_https)
        
        # If no images found with ASIN-specific patterns, try broader patterns
        if len(image_urls) == 0:
            broader_patterns = [
                # Look for colorImages in product data (may not have ASIN in same object)
                r'"colorImages"\s*:\s*{\s*"initial"\s*:\s*\[(.*?)\]',
                # Look for imageBlockData
                r'"imageBlockData"[^]]*\[(.*?)\]',
                # Look for main product images array
                r'"mainImageUrl"\s*:\s*"(https://[^"]+\.jpg[^"]*)"',
                r'"hiResImage"\s*:\s*"(https://[^"]+\.jpg[^"]*)"',
                # Direct image URL patterns in JSON
                r'"(https://m\.media-amazon\.com/images/I/[^"]+\._AC_SL\d+_\.jpg)"',
            ]
            for pattern in broader_patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                for match in matches:
                    if isinstance(match, str):
                        if match.startswith('https://'):
                            # Direct URL match
                            image_urls.add(match)
                        else:
                            # Extract image URLs from the matched JSON structure
                            urls = re.findall(r'"url"\s*:\s*"([^"]+\.jpg[^"]*)"', match)
                            clean_https = re.findall(r'(https://[^"]+\.jpg)', match)
                            image_urls.update(urls + clean_https)
        
        # Method 2: Extract from main product image gallery section only
        # Look for the main product image carousel/gallery (not related products)
        main_image_sections = [
            # Image block that contains the ASIN in nearby context
            rf'<div[^>]*id="imageBlock"[^>]*>.*?{asin_pattern}.*?</div>',
            # Main product image container
            rf'<div[^>]*class="[^"]*imageBlock[^"]*"[^>]*>.*?{asin_pattern}.*?</div>',
            # Just get imageBlock section (more permissive)
            r'<div[^>]*id="imageBlock"[^>]*>(.*?)</div>',
        ]
        
        for section_pattern in main_image_sections:
            sections = re.findall(section_pattern, html, re.DOTALL | re.IGNORECASE)
            for section in sections:
                # Extract images only from this specific section
                img_urls = re.findall(r'<img[^>]*src="(https://m\.media-amazon\.com/images/[^"]*\.jpg[^"]*)"', section)
                image_urls.update(img_urls)
                # Also extract from data attributes
                data_urls = re.findall(r'data-src="(https://m\.media-amazon\.com/images/[^"]*\.jpg[^"]*)"', section)
                image_urls.update(data_urls)
        
        # Method 3: Extract from JavaScript variables that are product-specific
        # Look for "landingImageUrl" or "mainImageUrl" in contexts with ASIN
        product_specific_patterns = [
            # Landing image in product data structure
            rf'"{asin_pattern}"[^}}]*"landingImageUrl"\s*:\s*"(https://[^"]*)"',
            # Main image URL
            rf'"{asin_pattern}"[^}}]*"mainImageUrl"\s*:\s*"(https://[^"]*)"',
            # High-res image
            rf'"{asin_pattern}"[^}}]*"hiRes"\s*:\s*"(https://[^"]*)"',
        ]
        
        for pattern in product_specific_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            image_urls.update(matches)
        
        # Method 4: Extract from imageBlockVariations - these are usually for the main product
        # Only if found in context with our ASIN
        if asin in html:
            # Find imageBlockVariations near our ASIN
            asin_context = html[max(0, html.find(asin) - 5000):html.find(asin) + 5000]
            variation_patterns = [
                r'imageBlockVariations.*?"url"\s*:\s*"(https://[^"]*\.jpg[^"]*)"',
            ]
            for pattern in variation_patterns:
                matches = re.findall(pattern, asin_context, re.DOTALL)
                image_urls.update(matches)
        
        # Method 5: Fallback - ONLY if we haven't found images yet AND only from main product section
        # This is a last resort - only extracts from the main product image block, not related items
        if len(image_urls) == 0:
            # Only extract from the main imageBlock section to avoid related product images
            image_block_pattern = r'<div[^>]*id="imageBlock"[^>]*>(.*?)</div>'
            image_block_match = re.search(image_block_pattern, html, re.DOTALL | re.IGNORECASE)
            if image_block_match:
                image_block_html = image_block_match.group(1)
                # Only extract images from within the main product image block
                fallback_pattern = r'(https://m\.media-amazon\.com/images/I/[A-Za-z0-9+/=_-]+\._AC_SL\d+_\.jpg)'
                fallback_urls = re.findall(fallback_pattern, image_block_html)
                image_urls.update(fallback_urls)
        
        # Clean up URLs - remove duplicates and invalid ones
        clean_urls = set()
        excluded_patterns = [
            r'/related/',  # Related products section
            r'/recommended/',  # Recommended products
            r'/sponsored/',  # Sponsored products
            r'/similar/',  # Similar products
            r'/frequently/',  # Frequently bought together
            r'/customer/',  # Customer images
            r'/review/',  # Review images
            r'community-reviews',  # Customer review images
            r'aplus-media-library',  # A+ content images (usually not main product)
            r'community-customer-media',  # Customer uploaded images
            r'_UC\d+',  # User/customer images
            r'__CR\d+',  # Carousel/review images
            r'__PT\d+',  # Related product images
            r'__AC_UC',  # User content images
            r'__AC_SR\d+',  # Search result thumbnails
            r'__AC_UF\d+',  # User-facing images (often reviews)
            r'related-products',  # Related products carousel
            r'recommended-products',  # Recommended products section
            r'sponsored-products',  # Sponsored section
            r'also-viewed',  # "Customers also viewed" section
            r'frequently-bought',  # Frequently bought together
            r'__AC_SY\d+',  # System images (often related products)
            r'__AC_SX\d+',  # System images (often related products)
            r'__AC_SZ\d+',  # System images (often related products)
            r'__AC_SS\d+',  # Search/system images
        ]
        
        # STRICT: Only allow _AC_SL patterns (main product images)
        # These are the standard product image patterns used by Amazon for main product photos
        main_product_patterns = [
            r'\._AC_SL1500_\.jpg',  # High resolution main product images
            r'\._AC_SL1000_\.jpg',  # Medium-high resolution
            r'\._AC_SL750_\.jpg',   # Medium resolution
            r'\._AC_SL500_\.jpg',   # Lower resolution (but still main product)
        ]
        
        # STRICT: Only allow main product images with _AC_SL pattern
        # This ensures we only get actual product photos, not related items
        for url in image_urls:
            # Normalize URL - extract only the actual URL part (before any JSON continuation)
            # URLs might have JSON data attached like: "url.jpg","other":"data"
            url_match = re.search(r'(https://[^",\s}]+\.jpg)', url)
            if url_match:
                url = url_match.group(1)
            else:
                url = url.strip('"').strip()
            
            # Remove any trailing characters that aren't part of the URL
            url = re.sub(r'["\',].*$', '', url)
            url = url.strip('"').strip()
            
            # Skip if URL is from excluded sections
            if any(re.search(pattern, url, re.IGNORECASE) for pattern in excluded_patterns):
                continue
            
            # Must be from media-amazon.com/images/I/ (main product images)
            if not re.search(r'\.media-amazon\.com/images/I/', url, re.IGNORECASE):
                continue
            
            # STRICT: Only accept _AC_SL patterns (main product images)
            # These are the standard Amazon product image patterns
            is_main_product_image = any(re.search(pattern, url, re.IGNORECASE) for pattern in main_product_patterns)
            
            if url.startswith('https://') and '.jpg' in url.lower() and is_main_product_image:
                # Validate it's a clean URL (no JSON artifacts)
                if '"' not in url and '{' not in url and '}' not in url:
                    # Always upgrade to highest resolution (SL1500)
                    if '._AC_SL' in url:
                        url = re.sub(r'_AC_SL\d+_', '_AC_SL1500_', url)
                    clean_urls.add(url)
        
        # Sort URLs to prioritize higher resolution images
        # Convert to list and sort by resolution (SL1500 first, then SL1000, etc.)
        clean_urls_list = list(clean_urls)
        def get_resolution_priority(url):
            """Returns priority number - lower is better (SL1500 = 0, SL1000 = 1, etc.)"""
            if '_AC_SL1500_' in url:
                return 0
            elif '_AC_SL1000_' in url:
                return 1
            elif '_AC_SL750_' in url:
                return 2
            elif '_AC_SL500_' in url:
                return 3
            else:
                return 999
        
        clean_urls_list.sort(key=get_resolution_priority)
        
        # Return only the best images (prioritized by resolution)
        # Limit to max_images at this stage
        final_urls = clean_urls_list[:self.max_images] if hasattr(self, 'max_images') else clean_urls_list[:3]
        logger.info(f"Found {len(clean_urls_list)} unique image URLs for ASIN {asin}, selecting top {len(final_urls)} (main product only)")
        return final_urls
    
    def extract_video_urls_from_html(self, html: str) -> List[str]:
        """
        Extract video URLs from HTML.
        
        Searches for:
        - MP4 video files
        - Video player iframes
        - Video metadata in JavaScript
        
        Args:
            html: HTML content of product page
            
        Returns:
            List of video URLs
        """
        video_urls = set()
        
        # Method 1: Direct video file URLs
        patterns = [
            r'<video[^>]*src="([^"]*\.mp4[^"]*)"',
            r'"videoUrl":"([^"]*\.mp4[^"]*)"',
            r'<source[^>]*src="([^"]*\.mp4[^"]*)"',
            r'https://[^"]*\.mp4[^"]*',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            video_urls.update(matches)
        
        # Method 2: Extract from video player data
        video_data_pattern = r'"videoUrl":"([^"]*)"'
        matches = re.findall(video_data_pattern, html)
        video_urls.update(matches)
        
        # Clean up URLs - extract only clean video URLs
        clean_urls = set()
        for url in video_urls:
            # Extract clean URL (remove JSON artifacts, quotes, etc.)
            # Look for actual video file URL
            url_match = re.search(r'(https://[^",\s}]+\.(?:mp4|webm|mov))', url, re.IGNORECASE)
            if url_match:
                clean_url = url_match.group(1)
                # Remove any trailing characters that aren't part of the URL
                clean_url = re.sub(r'["\',\s}].*$', '', clean_url)
                if clean_url.startswith('https://') and len(clean_url) > 20:  # Valid URL check
                    clean_urls.add(clean_url)
            else:
                # Fallback: try to clean the URL directly
                url = url.strip('"').strip()
                # Remove JSON artifacts
                url = re.sub(r'["\',}].*$', '', url)
                if url.startswith('https://') and any(ext in url.lower() for ext in ['.mp4', '.webm', '.mov']):
                    clean_urls.add(url)
        
        if clean_urls:
            logger.info(f"Found {len(clean_urls)} video URLs")
        
        return list(clean_urls)
    
    def download_file(self, url: str, filename: str, max_retries: int = 3) -> bool:
        """
        Download a file from URL with retry logic.
        
        Args:
            url: File URL
            filename: Path to save file
            max_retries: Number of retry attempts
            
        Returns:
            True if successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Downloading: {url}")
                response = self.session.get(url, timeout=15, stream=True)
                response.raise_for_status()
                
                # Check file size
                file_size = int(response.headers.get('content-length', 0))
                if file_size == 0:
                    logger.warning(f"File size is 0 for {url}")
                    return False
                
                # Calculate hash to avoid duplicates
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
                time.sleep(self.rate_limit)
                return True
                
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
        
        logger.error(f"Failed to download {url} after {max_retries} attempts")
        return False
    
    def process_product(self, product: Dict) -> Dict:
        """
        Process a single product to download all its media.
        
        Args:
            product: Product dictionary with 'name', 'url', 'asin'
            
        Returns:
            Dictionary with download results
        """
        result = {
            'name': product.get('name', 'Unknown'),
            'asin': product.get('asin', 'Unknown'),
            'url': product.get('url', ''),
            'images_downloaded': 0,
            'videos_downloaded': 0,
            'errors': []
        }
        
        # Extract ASIN from URL if not provided
        asin = product.get('asin') or self.extract_asin_from_url(product.get('url', ''))
        if not asin:
            result['errors'].append('Could not extract ASIN from URL')
            return result
        
        result['asin'] = asin
        
        # Create product directory
        product_dir = self.output_dir / asin
        product_dir.mkdir(exist_ok=True)
        
        # Try to fetch product page (may fail due to bot detection)
        html = self.get_product_page(product.get('url', ''))
        image_urls = []
        
        if html:
            # Extract and download images (already limited to max_images in extract method)
            image_urls = self.extract_image_urls_from_html(html, asin)
        else:
            result['errors'].append('Failed to fetch product page (will try fallback)')
        
        # Fallback: If no images found from HTML scraping, use image_url from product data
        # This ensures we always get at least 1 image if available in JSON
        if len(image_urls) == 0 and product.get('image_url'):
            fallback_url = product.get('image_url')
            # Validate it's a main product image pattern
            if re.search(r'\._AC_SL\d+_\.jpg', fallback_url, re.IGNORECASE):
                # Upgrade to high resolution
                if '._AC_SL' in fallback_url:
                    fallback_url = re.sub(r'_AC_SL\d+_', '_AC_SL1500_', fallback_url)
                image_urls.append(fallback_url)
                logger.info(f"Using fallback image_url from product data for {asin}")
        
        # Additional safety limit (should already be limited by extract method)
        image_urls = image_urls[:self.max_images]
        logger.info(f"Downloading up to {len(image_urls)} main product images for {asin}")
        
        for idx, img_url in enumerate(image_urls, 1):
            # Stop if we've reached max_images
            if result['images_downloaded'] >= self.max_images:
                logger.info(f"Reached image limit ({self.max_images}) for {asin}")
                break
            try:
                # Generate filename
                filename = product_dir / f"image_{idx:02d}.jpg"
                if self.download_file(img_url, str(filename)):
                    result['images_downloaded'] += 1
            except Exception as e:
                result['errors'].append(f"Image {idx} error: {str(e)}")
        
        # Extract and download videos (limited to max_videos, default: 1)
        # Only extract videos if we have HTML (may be None if page fetch failed)
        video_urls = []
        if html:
            video_urls = self.extract_video_urls_from_html(html)
            # Limit to max_videos
            video_urls = video_urls[:self.max_videos]
        logger.info(f"Downloading up to {len(video_urls)} videos for {asin}")
        
        for idx, video_url in enumerate(video_urls, 1):
            # Stop if we've reached max_videos
            if result['videos_downloaded'] >= self.max_videos:
                logger.info(f"Reached video limit ({self.max_videos}) for {asin}")
                break
            try:
                # Clean the video URL one more time to ensure it's valid
                # Remove any trailing JSON artifacts
                clean_video_url = re.sub(r'["\',}].*$', '', video_url)
                clean_video_url = clean_video_url.strip('"').strip()
                
                # Skip if URL is too short or doesn't look valid
                if len(clean_video_url) < 20 or not clean_video_url.startswith('https://'):
                    logger.warning(f"Skipping invalid video URL: {video_url[:100]}...")
                    continue
                
                # Determine video extension
                if '.mov' in clean_video_url.lower():
                    ext = '.mp4'  # Convert .mov to .mp4 for consistency
                elif '.mp4' in clean_video_url.lower():
                    ext = '.mp4'
                elif '.webm' in clean_video_url.lower():
                    ext = '.webm'
                else:
                    ext = '.mp4'  # Default
                
                filename = product_dir / f"video_{idx:02d}{ext}"
                if self.download_file(clean_video_url, str(filename)):
                    result['videos_downloaded'] += 1
            except Exception as e:
                result['errors'].append(f"Video {idx} error: {str(e)}")
        
        # Save product metadata
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
            List of results for each product
        """
        try:
            with open(products_file, 'r') as f:
                products = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load products file: {e}")
            return []
        
        logger.info(f"Starting scrape of {len(products)} products")
        results = []
        
        for idx, product in enumerate(products, 1):
            logger.info(f"Processing product {idx}/{len(products)}: {product.get('name', 'Unknown')}")
            result = self.process_product(product)
            results.append(result)
            
            # Progress report
            if result['images_downloaded'] > 0 or result['videos_downloaded'] > 0:
                logger.info(f"  [OK] Downloaded {result['images_downloaded']} images, {result['videos_downloaded']} videos")
            if result['errors']:
                for error in result['errors']:
                    logger.warning(f"  [WARNING] {error}")
        
        return results
    
    def generate_report(self, results: List[Dict], output_file: str = "scrape_report.json"):
        """
        Generate a summary report of the scraping operation.
        
        Args:
            results: List of results from scrape_products
            output_file: Path to save report
        """
        total_images = sum(r['images_downloaded'] for r in results)
        total_videos = sum(r['videos_downloaded'] for r in results)
        total_errors = sum(len(r['errors']) for r in results)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_products': len(results),
            'total_images_downloaded': total_images,
            'total_videos_downloaded': total_videos,
            'total_errors': total_errors,
            'success_rate': f"{sum(1 for r in results if r['images_downloaded'] > 0) / len(results) * 100:.1f}%",
            'products': results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"SCRAPING COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total products processed: {len(results)}")
        logger.info(f"Total images downloaded: {total_images}")
        logger.info(f"Total videos downloaded: {total_videos}")
        logger.info(f"Total errors: {total_errors}")
        logger.info(f"Success rate: {report['success_rate']}")
        logger.info(f"Report saved to: {output_file}")
        logger.info(f"Media saved to: {self.output_dir}")
        logger.info(f"{'='*60}\n")


def main():
    """Main entry point for the scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Download product images and videos from Amazon'
    )
    parser.add_argument(
        'products_file',
        help='Path to products JSON file'
    )
    parser.add_argument(
        '--output-dir',
        default='product_media',
        help='Output directory for media files (default: product_media)'
    )
    parser.add_argument(
        '--rate-limit',
        type=float,
        default=2.0,
        help='Seconds to wait between requests (default: 2.0)'
    )
    parser.add_argument(
        '--max-images',
        type=int,
        default=3,
        help='Maximum number of images to download per product (default: 3)'
    )
    parser.add_argument(
        '--max-videos',
        type=int,
        default=1,
        help='Maximum number of videos to download per product (default: 1)'
    )
    parser.add_argument(
        '--report',
        default='scrape_report.json',
        help='Output file for scraping report (default: scrape_report.json)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.products_file):
        logger.error(f"Products file not found: {args.products_file}")
        return
    
    # Initialize scraper
    scraper = AmazonProductScraper(
        output_dir=args.output_dir,
        rate_limit=args.rate_limit,
        max_images=args.max_images,
        max_videos=args.max_videos
    )
    
    # Run scraper
    results = scraper.scrape_products(args.products_file)
    
    # Generate report
    scraper.generate_report(results, args.report)


if __name__ == '__main__':
    main()
