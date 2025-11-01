import json
import os

# Define the paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, '..'))
PRODUCT_DATA_PATH = os.path.join(PROJECT_ROOT, "products-simple.json")
MEDIA_DIR = os.path.join(PROJECT_ROOT, "public", "product_media")

def analyze_media():
    print("=" * 80)
    print("PRODUCT MEDIA ANALYSIS REPORT")
    print("=" * 80)
    
    try:
        with open(PRODUCT_DATA_PATH, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print(f"Error: Product data file not found at {PRODUCT_DATA_PATH}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {PRODUCT_DATA_PATH}")
        return

    total_products = len(products)
    
    # Analysis metrics
    products_with_local_images = 0
    products_with_3_images = 0
    products_with_local_videos = 0
    products_meeting_full_requirement = []
    
    # Detailed analysis
    image_counts = []
    video_counts = []
    
    for product in products:
        local_images = product.get("local_images", [])
        local_videos = product.get("local_videos", [])
        
        if local_images:
            products_with_local_images += 1
            image_counts.append(len(local_images))
            if len(local_images) >= 3:
                products_with_3_images += 1
        
        if local_videos:
            products_with_local_videos += 1
            video_counts.append(len(local_videos))
        
        if len(local_images) >= 3 and len(local_videos) >= 1:
            products_meeting_full_requirement.append(product)
    
    # Print summary
    print(f"\nTotal Products: {total_products}")
    print("\n" + "-" * 80)
    print("MEDIA AVAILABILITY SUMMARY")
    print("-" * 80)
    print(f"Products with any local images:        {products_with_local_images:3d} ({products_with_local_images/total_products*100:.1f}%)")
    print(f"Products with 3+ local images:         {products_with_3_images:3d} ({products_with_3_images/total_products*100:.1f}%)")
    print(f"Products with any local videos:        {products_with_local_videos:3d} ({products_with_local_videos/total_products*100:.1f}%)")
    print(f"Products meeting full requirement:     {len(products_meeting_full_requirement):3d} ({len(products_meeting_full_requirement)/total_products*100:.1f}%)")
    
    if image_counts:
        print(f"\nAverage images per product (with images): {sum(image_counts)/len(image_counts):.1f}")
        print(f"Max images for a single product:          {max(image_counts)}")
    
    if video_counts:
        print(f"\nAverage videos per product (with videos): {sum(video_counts)/len(video_counts):.1f}")
        print(f"Max videos for a single product:          {max(video_counts)}")
    
    # Products meeting requirements
    print("\n" + "-" * 80)
    print("PRODUCTS MEETING FULL REQUIREMENT (3+ images AND 1+ video)")
    print("-" * 80)
    if products_meeting_full_requirement:
        for product in products_meeting_full_requirement:
            img_count = len(product.get("local_images", []))
            vid_count = len(product.get("local_videos", []))
            print(f"  • {product['name'][:60]}")
            print(f"    ASIN: {product['asin']} | Images: {img_count} | Videos: {vid_count}")
    else:
        print("  None found.")
    
    # Products with 3+ images but no videos
    print("\n" + "-" * 80)
    print("PRODUCTS WITH 3+ IMAGES BUT NO VIDEOS")
    print("-" * 80)
    products_with_images_no_videos = [p for p in products if len(p.get("local_images", [])) >= 3 and len(p.get("local_videos", [])) == 0]
    if products_with_images_no_videos:
        for product in products_with_images_no_videos[:5]:
            print(f"  • {product['name'][:60]}")
            print(f"    ASIN: {product['asin']} | Images: {len(product.get('local_images', []))}")
    else:
        print("  None found.")
    
    # Products with only 1-2 images
    print("\n" + "-" * 80)
    print("PRODUCTS WITH 1-2 IMAGES ONLY")
    print("-" * 80)
    products_with_few_images = [p for p in products if len(p.get("local_images", [])) in [1, 2]]
    if products_with_few_images:
        print(f"  Total: {len(products_with_few_images)} products")
        for product in products_with_few_images[:5]:
            print(f"  • {product['name'][:60]}")
            print(f"    ASIN: {product['asin']} | Images: {len(product.get('local_images', []))}")
        if len(products_with_few_images) > 5:
            print(f"  ... and {len(products_with_few_images) - 5} more")
    
    # Overall assessment
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    if products_with_local_images < total_products * 0.5:
        print("[WARNING] Low image coverage: Most products lack local images.")
        print("   Action: Run scraping scripts to download product images.")
    
    if len(products_meeting_full_requirement) < 3:
        print("[WARNING] Few products meet the full media requirement (3+ images, 1+ video).")
        print("   Action: Prioritize these products for media enhancement.")
    
    if len(products_with_few_images) > 0:
        print(f"[WARNING] {len(products_with_few_images)} products have only 1-2 images.")
        print("   Action: Add more images to meet the 3+ image requirement.")
    
    print("\n[SUCCESS] Media update script has been integrated.")
    print("   Run 'python scripts/update_media_links.py' after adding new media files.")
    print("=" * 80)

if __name__ == "__main__":
    analyze_media()

