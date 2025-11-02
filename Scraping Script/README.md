# Amazon Product Scraper - Main Guide

This directory contains scripts and tools for downloading product images from Amazon.

## Quick Start

See **GET_ALL_IMAGES.md** for step-by-step instructions.

Quick reference: **QUICK_START.txt**

## Available Scripts

### Main Scrapers
- **`amazon_product_scraper.py`** - Main scraper (recommended)
  ```bash
  python amazon_product_scraper.py products-simple.json
  ```

- **`amazon_product_scraper_selenium.py`** - Advanced scraper (uses browser automation)
  ```bash
  python amazon_product_scraper_selenium.py products-simple.json
  ```

- **`batch_scraper.py`** - Batch processor (can resume if interrupted)
  ```bash
  python batch_scraper.py products-simple.json --batch-size 25
  ```

### Utility Scripts
- **`update_json_with_local_images.py`** - Update JSON with local image paths
- **`cleanup_non_catalog.py`** - Remove images for products not in catalog

## Documentation

- **GET_ALL_IMAGES.md** - Complete guide on downloading images
- **QUICK_START.txt** - Quick reference card
- **Amazon Product Image & Video Scraper.md** - Detailed technical documentation

## Output

All images are saved to `product_media/` directory organized by product ASIN.

