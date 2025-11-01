# Media Management Scripts

This directory contains Python scripts for analyzing and managing product media in your store.

## Quick Start

Need to download missing images? Run:
```bash
python scripts/run_missing_images_download.py
cd 'Scraping Script'
python batch_scraper.py ../batch_missing_images.json --batch-size 25 --max-images 3
cd ..
npm run media:update
```

Want to analyze current media? Run:
```bash
npm run media:analyze
```

## Scripts

### 1. `update_media_links.py`

**Purpose:** Synchronizes local media files with the product data JSON file.

**What it does:**
- Scans the `public/product_media` directory for image and video files
- Updates the `products-simple.json` file with `local_images` and `local_videos` arrays
- Adds `image_count` and `video_count` fields for each product
- Ensures data consistency between files on disk and the JSON data

**When to run:**
- After downloading new product images or videos
- After manually adding media files to `public/product_media/{ASIN}/`
- Before deploying to ensure all local media is properly linked

**Usage:**
```bash
# Using npm
npm run media:update

# Or directly with Python
python scripts/update_media_links.py
```

### 2. `analyze_media.py`

**Purpose:** Generates a comprehensive report on product media availability.

**What it does:**
- Analyzes media coverage across all products
- Identifies products meeting the full requirement (3+ images, 1+ video)
- Highlights products needing additional media
- Provides statistics and recommendations

**Usage:**
```bash
# Using npm
npm run media:analyze

# Or directly with Python
python scripts/analyze_media.py
```

**Sample Output:**
```
================================================================================
PRODUCT MEDIA ANALYSIS REPORT
================================================================================

Total Products: 108

--------------------------------------------------------------------------------
MEDIA AVAILABILITY SUMMARY
--------------------------------------------------------------------------------
Products with any local images:          7 (6.5%)
Products with 3+ local images:           3 (2.8%)
Products with any local videos:         11 (10.2%)
Products meeting full requirement:       3 (2.8%)
```

### 3. `run_missing_images_download.py` ⭐ **NEW**

**Purpose:** Download missing images for products that have 0-2 images.

**What it does:**
- Identifies products needing more images
- Creates batch file for scraper
- Downloads maximum 3 images per product (practical limit)
- Integrates with existing scraper infrastructure

**Usage:**
```bash
# Step 1: Prepare batch file
python scripts/run_missing_images_download.py

# Step 2: Download images (choose one method)
cd 'Scraping Script'
python batch_scraper.py ../batch_missing_images.json --batch-size 25 --max-images 3

# Step 3: Update JSON
cd ..
npm run media:update

# Step 4: Verify
npm run media:analyze
```

**Why 3 images?**
- Carousel displays 3-5 images effectively
- Prevents excessive disk usage
- Faster loading times
- Better user experience

## Recommended Workflow

### After Scraping New Media

1. **Run the update script** to sync new files with JSON:
   ```bash
   npm run media:update
   ```

2. **Run the analysis script** to verify results:
   ```bash
   npm run media:analyze
   ```

3. **Review recommendations** for products that need more media

### Before Deployment

Always run both scripts before deploying to production:

```bash
npm run media:update && npm run media:analyze
```

This ensures:
- All media files are properly linked in JSON
- You have visibility into media coverage
- No orphaned files or missing links

## Media Requirements

**Target:** Each product should have:
- **3+ images** for the carousel
- **1+ video** for enhanced showcasing

Products meeting this requirement will display properly in the `ProductImageCarousel` component.

## File Structure

Media files should follow this structure:

```
public/
  product_media/
    {ASIN}/
      image_01.jpg
      image_02.jpg
      image_03.jpg
      video_01.mp4
      metadata.json (optional)
```

**Supported formats:**
- Images: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`
- Videos: `.mp4`, `.webm`, `.mov`

## Integration with Scraping

If you have scraping scripts in the `Scraping Script/` directory, consider integrating the `update_media_links.py` logic:

1. Run scraping script to download media
2. Automatically call `update_media_links.py` 
3. Verify with `analyze_media.py`

This ensures data synchronization after every scraping session.

## Troubleshooting

### No local images showing

1. Check if files exist in `public/product_media/{ASIN}/`
2. Run `npm run media:update` to re-sync
3. Restart dev server to reload JSON

### Missing media files

1. Run `npm run media:analyze` to identify gaps
2. Prioritize popular or featured products
3. Use scraping scripts to download missing media

### Path issues on Windows

The scripts handle Windows path separators automatically. If you encounter issues, ensure paths use forward slashes in JSON.

