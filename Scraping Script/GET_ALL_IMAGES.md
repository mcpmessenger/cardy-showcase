# How to Get Images for All Products in Your Catalog

## Quick Start (Easiest Method)

### Step 1: Navigate to the Scraping Script directory
```bash
cd "Scraping Script"
```

### Step 2: Run the scraper
```bash
python amazon_product_scraper.py products-simple.json
```

That's it! This will:
- Download **up to 10 images** per product (focuses on photos)
- Download **1 video** per product (if available)
- Save them in `product_media/` folder organized by ASIN
- Generate a report showing what was downloaded
- Take approximately **3-5 hours** (with rate limiting to avoid IP blocks)

**Note**: By default, the scraper limits to 10 images and 1 video per product to keep downloads manageable. You can adjust these limits with `--max-images` and `--max-videos` options.

---

## Recommended: Use Batch Processing

For better reliability and ability to resume if interrupted:

### Method 1: Use the Batch Scraper
```bash
cd "Scraping Script"
python batch_scraper.py products-simple.json --batch-size 25
```

This splits your 108 products into batches of 25 and processes them safely.

### Method 2: If You Get Blocked, Increase Rate Limit
If Amazon blocks your requests (403 errors), slow down:

```bash
python amazon_product_scraper.py products-simple.json --rate-limit 5.0
```

This waits 5 seconds between requests instead of 2 seconds.

---

## After Downloading Images

### Step 1: Update the JSON file with local image paths
```bash
python update_json_with_local_images.py
```

This updates `products-simple.json` to reference the downloaded images.

### Step 2: Copy images to public folder for your website
```powershell
# From the Store root directory
Copy-Item -Path "Scraping Script\product_media" -Destination "public\product_media" -Recurse -Force
```

### Step 3: Copy updated JSON to root
```powershell
Copy-Item -Path "Scraping Script\products-simple.json" -Destination "products-simple.json" -Force
```

---

## What Each Method Does

| Method | Pros | Cons | Time Estimate |
|--------|------|------|---------------|
| `amazon_product_scraper.py` | Simple, straightforward | No resume capability | 6-9 hours |
| `batch_scraper.py` | Can resume, safer | More complex | 6-9 hours |
| `amazon_product_scraper_selenium.py` | Most reliable, handles JS | Requires ChromeDriver, slowest | 12+ hours |

---

## Prerequisites

Make sure you have Python packages installed:
```bash
pip install requests beautifulsoup4 pillow
```

For Selenium version (optional, more reliable):
```bash
pip install selenium webdriver-manager
```

---

## Troubleshooting

### "403 Forbidden" Error
**Solution**: Increase rate limit
```bash
python amazon_product_scraper.py products-simple.json --rate-limit 10.0
```

### "Connection timeout"
**Solution**: Check internet connection, try again later

### "Module not found"
**Solution**: Install missing packages
```bash
pip install requests beautifulsoup4 pillow
```

### Images not downloading
**Solution**: Check `scraper.log` file for detailed error messages

---

## Progress Monitoring

While scraping, you can monitor progress:

```bash
# Watch the log file in real-time (Linux/Mac)
tail -f scraper.log

# Or check the product_media folder
# You'll see folders being created as products are processed
```

---

## Resuming After Interruption

If the scraper stops:

1. **Using batch_scraper**: Resume from a specific batch
   ```bash
   python batch_scraper.py products-simple.json --resume-from 3
   ```

2. **Using regular scraper**: It will skip products that already have images downloaded

---

## Expected Results

After completion, you'll have:
- `product_media/` folder with 108 product folders
- Each folder contains:
  - `image_01.jpg`, `image_02.jpg`, etc. (product photos)
  - `metadata.json` (product info)
  - `video_01.mp4`, etc. (if videos available)
- `scrape_report.json` (summary of what was downloaded)

---

## Time Estimates

- **Full 108 products**: 6-9 hours (with 2-3 second rate limit)
- **Per product**: ~3-5 minutes average
- **If blocked**: May take longer, need to increase delays

---

## Next Steps After Download

1. ✅ Run `update_json_with_local_images.py` to update JSON
2. ✅ Copy images to `public/product_media/`
3. ✅ Copy updated JSON to root directory
4. ✅ Restart your web server
5. ✅ Verify images display on your website

---

**Tip**: Start with a test run on just a few products first:
```bash
# Create a test file with 5 products
# Then run: python amazon_product_scraper.py test_products.json
```

