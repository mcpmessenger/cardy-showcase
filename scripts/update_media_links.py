import json
import os

# Define the paths - using relative paths for portability
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) # Script directory
PROJECT_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, '..')) # Go up one level to project root
PRODUCT_DATA_PATH = os.path.join(PROJECT_ROOT, "products-simple.json")
MEDIA_DIR_NAME = "product_media"
MEDIA_DIR = os.path.join(PROJECT_ROOT, "public", MEDIA_DIR_NAME)

# Define supported file extensions
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
VIDEO_EXTENSIONS = ('.mp4', '.webm', '.mov')

def update_product_media_links():
    print(f"Loading product data from: {PRODUCT_DATA_PATH}")
    try:
        with open(PRODUCT_DATA_PATH, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print(f"Error: Product data file not found at {PRODUCT_DATA_PATH}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {PRODUCT_DATA_PATH}")
        return

    print(f"Scanning media directory: {MEDIA_DIR}")
    if not os.path.exists(MEDIA_DIR):
        print(f"Error: Media directory not found at {MEDIA_DIR}")
        return

    updated_count = 0
    
    # Get a list of all ASIN directories in the media folder
    asin_dirs = [d for d in os.listdir(MEDIA_DIR) if os.path.isdir(os.path.join(MEDIA_DIR, d))]

    for product in products:
        asin = product.get("asin")
        
        if asin and asin in asin_dirs:
            asin_path = os.path.join(MEDIA_DIR, asin)
            
            local_images = []
            local_videos = []
            
            # Scan files in the ASIN directory
            for filename in os.listdir(asin_path):
                # The path stored in JSON must be relative to the 'public' folder for the app to find it
                file_path = os.path.join(MEDIA_DIR_NAME, asin, filename).replace('\\', '/')
                
                if filename.lower().endswith(IMAGE_EXTENSIONS):
                    local_images.append(file_path)
                elif filename.lower().endswith(VIDEO_EXTENSIONS):
                    local_videos.append(file_path)
            
            # Sort for consistent order
            local_images.sort()
            local_videos.sort()
            
            # Update product object
            if local_images:
                product["local_images"] = local_images
                product["image_count"] = len(local_images)
            else:
                # Ensure the field is removed if no images are found to keep the JSON clean
                product.pop("local_images", None)
                product.pop("image_count", None)
            
            if local_videos:
                product["local_videos"] = local_videos
                product["video_count"] = len(local_videos)
            else:
                product.pop("local_videos", None)
                product.pop("video_count", None)
            
            if local_images or local_videos:
                updated_count += 1

    print(f"Finished scanning. Updated {updated_count} products with local media links.")
    
    # Write the updated JSON back to the file
    try:
        with open(PRODUCT_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        print(f"Successfully wrote updated data back to {PRODUCT_DATA_PATH}")
    except Exception as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    update_product_media_links()

