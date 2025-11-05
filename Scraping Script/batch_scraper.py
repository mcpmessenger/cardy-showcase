#!/usr/bin/env python3
"""
Batch Product Scraper
=====================

This script splits your products into batches and scrapes them sequentially.
This approach is safer and allows you to resume if something goes wrong.

Usage:
    python batch_scraper.py products-simple.json --batch-size 25
"""

import json
import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchScraper:
    """
    Splits products into batches and scrapes them sequentially.
    """
    
    def __init__(self, batch_size: int = 25, rate_limit: float = 2.0, 
                 max_images: int = 3, max_videos: int = 1):
        """
        Initialize batch scraper.
        
        Args:
            batch_size: Number of products per batch
            rate_limit: Rate limit for each batch
            max_images: Maximum images per product (default: 3 - just a couple good images)
            max_videos: Maximum videos per product (default: 1)
        """
        self.batch_size = batch_size
        self.rate_limit = rate_limit
        self.max_images = max_images
        self.max_videos = max_videos
        self.batches_dir = Path("product_batches")
        self.batches_dir.mkdir(exist_ok=True)
    
    def split_products(self, products_file: str) -> List[str]:
        """
        Split products into batch files.
        
        Args:
            products_file: Path to products JSON
            
        Returns:
            List of batch file paths
        """
        try:
            with open(products_file, 'r') as f:
                products = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load products: {e}")
            return []
        
        logger.info(f"Splitting {len(products)} products into batches of {self.batch_size}")
        
        batch_files = []
        for batch_num, i in enumerate(range(0, len(products), self.batch_size), 1):
            batch = products[i:i + self.batch_size]
            batch_file = self.batches_dir / f"batch_{batch_num:03d}.json"
            
            with open(batch_file, 'w') as f:
                json.dump(batch, f, indent=2)
            
            batch_files.append(str(batch_file))
            logger.info(f"Created {batch_file} with {len(batch)} products")
        
        return batch_files
    
    def scrape_batch(self, batch_file: str, batch_num: int, total_batches: int) -> bool:
        """
        Scrape a single batch.
        
        Args:
            batch_file: Path to batch JSON file
            batch_num: Batch number
            total_batches: Total number of batches
            
        Returns:
            True if successful
        """
        output_dir = f"product_media_batch_{batch_num:03d}"
        report_file = f"batch_{batch_num:03d}_report.json"
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing Batch {batch_num}/{total_batches}")
        logger.info(f"{'='*60}")
        logger.info(f"Input: {batch_file}")
        logger.info(f"Output: {output_dir}")
        logger.info(f"Report: {report_file}")
        
        try:
            cmd = [
                'python',
                'amazon_product_scraper.py',
                batch_file,
                '--output-dir', output_dir,
                '--rate-limit', str(self.rate_limit),
                '--max-images', str(self.max_images),
                '--max-videos', str(self.max_videos),
                '--report', report_file
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=False)
            
            logger.info(f"✓ Batch {batch_num} completed successfully")
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Batch {batch_num} failed with error code {e.returncode}")
            return False
        except Exception as e:
            logger.error(f"✗ Batch {batch_num} failed: {e}")
            return False
    
    def run(self, products_file: str, resume_from: int = 1) -> Dict:
        """
        Run batch scraping.
        
        Args:
            products_file: Path to products JSON
            resume_from: Resume from batch number (for resuming interrupted runs)
            
        Returns:
            Summary dictionary
        """
        # Split products into batches
        batch_files = self.split_products(products_file)
        if not batch_files:
            logger.error("No batches created")
            return {}
        
        total_batches = len(batch_files)
        successful_batches = 0
        failed_batches = []
        
        logger.info(f"\nStarting batch scraping: {total_batches} batches")
        logger.info(f"Batch size: {self.batch_size} products")
        logger.info(f"Rate limit: {self.rate_limit} seconds")
        
        start_time = time.time()
        
        for batch_num, batch_file in enumerate(batch_files, 1):
            if batch_num < resume_from:
                logger.info(f"Skipping batch {batch_num} (resuming from {resume_from})")
                continue
            
            success = self.scrape_batch(batch_file, batch_num, total_batches)
            
            if success:
                successful_batches += 1
            else:
                failed_batches.append(batch_num)
            
            # Wait between batches to avoid IP blocks
            if batch_num < total_batches:
                wait_time = 30  # 30 seconds between batches
                logger.info(f"Waiting {wait_time} seconds before next batch...")
                time.sleep(wait_time)
        
        elapsed_time = time.time() - start_time
        
        # Generate summary
        summary = {
            'total_batches': total_batches,
            'successful_batches': successful_batches,
            'failed_batches': failed_batches,
            'success_rate': f"{successful_batches / total_batches * 100:.1f}%",
            'elapsed_time_seconds': int(elapsed_time),
            'elapsed_time_minutes': f"{elapsed_time / 60:.1f}",
            'batch_files': batch_files
        }
        
        return summary
    
    def print_summary(self, summary: Dict):
        """Print summary of batch scraping."""
        logger.info(f"\n{'='*60}")
        logger.info(f"BATCH SCRAPING COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total batches: {summary['total_batches']}")
        logger.info(f"Successful: {summary['successful_batches']}")
        logger.info(f"Failed: {len(summary['failed_batches'])}")
        logger.info(f"Success rate: {summary['success_rate']}")
        logger.info(f"Time elapsed: {summary['elapsed_time_minutes']} minutes")
        
        if summary['failed_batches']:
            logger.warning(f"Failed batches: {summary['failed_batches']}")
            logger.warning(f"To retry failed batches, run:")
            for batch_num in summary['failed_batches']:
                logger.warning(f"  python batch_scraper.py products-simple.json --resume-from {batch_num}")
        
        logger.info(f"{'='*60}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Split products into batches and scrape them safely'
    )
    parser.add_argument(
        'products_file',
        help='Path to products JSON file'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=25,
        help='Number of products per batch (default: 25)'
    )
    parser.add_argument(
        '--rate-limit',
        type=float,
        default=2.0,
        help='Rate limit in seconds (default: 2.0)'
    )
    parser.add_argument(
        '--max-images',
        type=int,
        default=3,
        help='Maximum images per product (default: 3 - just a couple good images)'
    )
    parser.add_argument(
        '--max-videos',
        type=int,
        default=1,
        help='Maximum videos per product (default: 1)'
    )
    parser.add_argument(
        '--resume-from',
        type=int,
        default=1,
        help='Resume from batch number (default: 1)'
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.products_file):
        logger.error(f"Products file not found: {args.products_file}")
        sys.exit(1)
    
    if not os.path.exists('amazon_product_scraper.py'):
        logger.error("amazon_product_scraper.py not found in current directory")
        sys.exit(1)
    
    # Run batch scraper
    scraper = BatchScraper(
        batch_size=args.batch_size,
        rate_limit=args.rate_limit,
        max_images=args.max_images,
        max_videos=args.max_videos
    )
    
    summary = scraper.run(args.products_file, resume_from=args.resume_from)
    scraper.print_summary(summary)


if __name__ == '__main__':
    main()
