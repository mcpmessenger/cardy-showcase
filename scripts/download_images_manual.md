# Manual Image Download Instructions

Since automated scraping may be blocked by Amazon, here are alternative ways to get product images:

## Option 1: Use Amazon Product Advertising API
If you have API access, you can get high-quality images directly.

## Option 2: Manual Download from Amazon Product Pages

1. Visit the product pages:
   - Paper Towels: https://www.amazon.com/dp/B09BWFX1L6
   - Toilet Paper: https://www.amazon.com/dp/B095CN96JS

2. Right-click on the main product image and "Save Image As..."

3. Save images to:
   - `public/product_media/B09BWFX1L6/image_01.jpg`
   - `public/product_media/B095CN96JS/image_01.jpg`

4. You can download multiple images (up to 5) and name them:
   - `image_01.jpg`, `image_02.jpg`, etc.

## Option 3: Use Browser Extension
- Install an image downloader extension
- Visit the product pages
- Download all images from the page
- Filter and save the main product images

## Option 4: Use the Scraping Script with Selenium
The Scraping Script folder has a Selenium-based scraper that can handle JavaScript-rendered content:

```bash
cd "Scraping Script"
python amazon_product_scraper_selenium.py products-simple.json
```

Note: This requires ChromeDriver to be installed.

