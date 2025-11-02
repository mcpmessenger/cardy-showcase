#!/usr/bin/env python3
"""
Clean up product_media directories that aren't in the catalog.
"""
import json
import os
import shutil
from pathlib import Path

def cleanup_non_catalog():
    """Remove directories for products not in catalog."""
    # Load catalog
    with open('products-simple.json', 'r') as f:
        products = json.load(f)
    
    catalog_asins = {p.get('asin') for p in products if p.get('asin')}
    print(f"Catalog contains {len(catalog_asins)} products")
    
    # Check product_media directory
    media_dir = Path('product_media')
    if not media_dir.exists():
        print("No product_media directory found")
        return
    
    # Find directories not in catalog
    all_dirs = [d for d in os.listdir(media_dir) if (media_dir / d).is_dir()]
    not_in_catalog = [d for d in all_dirs if d not in catalog_asins]
    
    if not not_in_catalog:
        print("[OK] All directories are in catalog - nothing to clean up")
        return
    
    print(f"\nFound {len(not_in_catalog)} directories not in catalog:")
    for asin in not_in_catalog:
        print(f"  - {asin}")
    
    # Remove them
    cleaned = 0
    for asin in not_in_catalog:
        dir_path = media_dir / asin
        try:
            shutil.rmtree(dir_path)
            print(f"[OK] Deleted {asin}")
            cleaned += 1
        except Exception as e:
            print(f"[ERROR] Failed to delete {asin}: {e}")
    
    print(f"\n[OK] Cleaned up {cleaned} directories")

if __name__ == '__main__':
    cleanup_non_catalog()

