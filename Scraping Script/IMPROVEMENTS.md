# Scraper Improvements - Image Filtering Update

## What Changed

The scraping scripts have been updated to address the issue of getting too many images or related product images. The scripts now:

1. **Limit to 2-3 images per product** (changed from 10)
2. **Strictly filter out related product images** - Only accepts `_AC_SL` patterns (main product images)
3. **Prioritize high-resolution images** - Automatically upgrades to SL1500 resolution
4. **Better exclusion patterns** - Filters out related products, customer reviews, sponsored items, etc.

## Updated Files

### 1. `amazon_product_scraper.py`
- Default `max_images` changed from 10 to **3**
- Added strict filtering to only accept `_AC_SL` patterns (main product images)
- Enhanced exclusion patterns for related products
- Images are sorted by resolution (highest quality first)

### 2. `batch_scraper.py`
- Updated default `max_images` from 10 to **3**
- Passes the limit to the main scraper

### 3. `quick_image_fetcher.py`
- Updated to fetch up to **3 images** per product (was 1)
- Uses the same strict filtering as the main scraper
- Prioritizes high-resolution images

## How to Use

### Basic Usage (Recommended)
```bash
cd "Scraping Script"
python amazon_product_scraper.py products-simple.json
```

This will download **up to 3 images** per product, focusing only on main product photos.

### Custom Image Limit
If you want a different number of images (e.g., 2 or 5):
```bash
python amazon_product_scraper.py products-simple.json --max-images 2
```

### Batch Processing (Safer)
```bash
python batch_scraper.py products-simple.json --batch-size 25 --max-images 3
```

### Quick Fetch (Fastest)
```bash
python quick_image_fetcher.py
```

This will fetch up to 3 images for products that don't have any images yet.

## What Gets Filtered Out

The scraper now excludes:
- Related product images
- Recommended product images
- Sponsored product images
- Customer review images
- User-uploaded images
- System/search images (`_AC_SY`, `_AC_SX`, `_AC_SZ`, `_AC_SS`)
- User content images (`_AC_UC`, `__AC_UF`)

## What Gets Included

Only main product images with these patterns:
- `_AC_SL1500_` (highest resolution - preferred)
- `_AC_SL1000_` (high resolution)
- `_AC_SL750_` (medium resolution)
- `_AC_SL500_` (lower resolution - fallback)

All images are automatically upgraded to SL1500 resolution when possible.

## Image Selection Priority

Images are selected in this order:
1. Highest resolution images first (SL1500)
2. Then lower resolutions if needed
3. Up to the maximum limit (default: 3)

## Expected Results

For 108 products, you can expect:
- **2-3 images per product** (instead of 10+)
- **Only main product photos** (no related items)
- **High-quality images** (SL1500 resolution)
- **Total: ~250-300 images** (instead of 1000+)

## Troubleshooting

### If you still get related product images:
1. Check the log file (`scraper.log`) to see which patterns matched
2. The scraper might need Amazon's HTML structure to change
3. Try the Selenium version for more reliable results:
   ```bash
   python amazon_product_scraper_selenium.py products-simple.json --max-images 3
   ```

### If images are missing:
- Some products may genuinely only have 1-2 images
- Check the product page manually to verify
- The scraper will log what it finds

## Next Steps

After running the scraper:
1. Run `update_json_with_local_images.py` to update the JSON file
2. Copy images to `public/product_media/` folder
3. Verify images display correctly on your website

---

**Note**: The scraper respects Amazon's rate limits. It waits 2-3 seconds between requests to avoid IP blocks. Be patient - scraping 108 products will take 3-5 hours.


