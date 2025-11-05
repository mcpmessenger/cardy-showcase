#!/usr/bin/env python3
"""
Remove products with 404 errors (failed image downloads) from products-simple.json
"""

import json
from pathlib import Path

def main():
    # Load the scrape report to find failed products
    report_file = Path("scrape_report.json")
    products_file = Path("products-simple.json")
    backup_file = Path("products-simple.json.backup")
    
    if not report_file.exists():
        print(f"Error: {report_file} not found. Run the scraper first.")
        return
    
    if not products_file.exists():
        print(f"Error: {products_file} not found.")
        return
    
    # Load scrape report
    print("Loading scrape report...")
    with open(report_file, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # Find products with no images downloaded (likely 404 errors)
    failed_asins = {p['asin'] for p in report['products'] if p['images_downloaded'] == 0}
    print(f"\nFound {len(failed_asins)} products with no images downloaded")
    
    # Load products JSON
    print(f"Loading {products_file}...")
    with open(products_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"Original products count: {len(products)}")
    
    # Create backup
    print(f"Creating backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    # Filter out failed products
    filtered_products = [p for p in products if p.get('asin') not in failed_asins]
    
    print(f"Filtered products count: {len(filtered_products)}")
    print(f"Removed {len(products) - len(filtered_products)} products with 404 errors")
    
    # Save updated products file
    print(f"Saving updated {products_file}...")
    with open(products_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_products, f, indent=2, ensure_ascii=False)
    
    # Show removed products
    removed_products = [p for p in products if p.get('asin') in failed_asins]
    print(f"\nRemoved products:")
    for i, product in enumerate(removed_products[:10], 1):
        print(f"  {i}. {product.get('name', 'Unknown')[:60]} (ASIN: {product.get('asin')})")
    if len(removed_products) > 10:
        print(f"  ... and {len(removed_products) - 10} more")
    
    print(f"\n[SUCCESS] Successfully removed {len(removed_products)} products with 404 errors")
    print(f"[SUCCESS] Backup saved to: {backup_file}")
    print(f"[SUCCESS] Updated products file: {products_file} ({len(filtered_products)} products)")

if __name__ == "__main__":
    main()

