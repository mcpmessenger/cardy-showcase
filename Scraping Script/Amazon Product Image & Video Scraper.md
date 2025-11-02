# Amazon Product Image & Video Scraper

A comprehensive Python toolkit for downloading product images and videos from Amazon product pages. This package includes multiple scraping strategies to handle different scenarios and maximize success rates.

## 📦 What's Included

### Core Scripts

1. **`amazon_product_scraper.py`** - Main scraper (recommended for most users)
   - Fast, lightweight, uses HTML parsing
   - Handles multiple images per product
   - Extracts high-resolution image variants
   - Includes retry logic and error handling
   - **Best for**: Quick scraping of large product lists

2. **`amazon_product_scraper_selenium.py`** - Advanced scraper with browser automation
   - Uses Selenium WebDriver for JavaScript-rendered content
   - Handles lazy-loaded images
   - Scrolls through image galleries
   - More robust but slower
   - **Best for**: Products with dynamic image loading

3. **`batch_scraper.py`** - Safe batch processing
   - Splits 108 products into manageable batches
   - Scrapes sequentially with delays between batches
   - Allows resuming if interrupted
   - **Best for**: Large product lists, avoiding IP blocks

### Documentation

- **`QUICK_START.md`** - Get started in 5 minutes
- **`SCRAPER_GUIDE.md`** - Comprehensive guide with troubleshooting
- **`README.md`** - This file

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Basic version (recommended)
pip install requests beautifulsoup4 pillow

# Advanced version with Selenium
pip install selenium webdriver-manager
```

### 2. Run the Scraper

```bash
# Simple: scrape all 108 products
python amazon_product_scraper.py products-simple.json

# Batch: safer approach for large lists
python batch_scraper.py products-simple.json --batch-size 25

# Advanced: use Selenium for better results
python amazon_product_scraper_selenium.py products-simple.json
```

### 3. Find Your Downloads

Images are saved in organized directories:
```
product_media/
├── B09XS7JWHH/
│   ├── image_01.jpg
│   ├── image_02.jpg
│   └── metadata.json
├── B0CHWRXH8B/
│   └── image_01.jpg
└── ...
```

## 📊 Comparison of Scraping Methods

| Feature | Basic | Selenium | Batch |
|---------|-------|----------|-------|
| Speed | ⚡⚡⚡ Fast | ⚡ Slow | ⚡⚡ Medium |
| Reliability | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very Good |
| IP Block Risk | ⚠️ Medium | ⚠️ Low | ✅ Very Low |
| Setup Complexity | ✅ Simple | ⚠️ Complex | ✅ Simple |
| JavaScript Support | ❌ No | ✅ Yes | ❌ No |
| Best For | Quick scraping | Complex pages | Large lists |

## 🔧 Usage Examples

### Example 1: Quick Test (5 products)

```bash
# Create a test file with first 5 products
python -c "
import json
with open('products-simple.json') as f:
    products = json.load(f)
with open('test_products.json', 'w') as f:
    json.dump(products[:5], f)
"

# Run scraper
python amazon_product_scraper.py test_products.json --output-dir test_media
```

### Example 2: Batch Processing (Safe)

```bash
# Process 108 products in batches of 25
python batch_scraper.py products-simple.json --batch-size 25 --rate-limit 3.0

# Resume if interrupted
python batch_scraper.py products-simple.json --resume-from 3
```

### Example 3: High-Quality Scraping

```bash
# Use Selenium for best results
python amazon_product_scraper_selenium.py products-simple.json --output-dir premium_media
```

### Example 4: Slow & Steady (Avoid Blocks)

```bash
# Increase rate limit to avoid IP blocks
python amazon_product_scraper.py products-simple.json --rate-limit 5.0
```

## 📈 Performance Tips

1. **Start Small**: Test with 5-10 products first
2. **Monitor Progress**: Watch the log file in real-time
   ```bash
   tail -f scraper.log
   ```
3. **Increase Rate Limit**: If blocked, increase `--rate-limit`
4. **Use Batches**: For 100+ products, use batch processing
5. **Run Off-Peak**: Scrape during late night/early morning
6. **Check Logs**: Review `scraper.log` for detailed information

## ⚠️ Important Notes

### Legal & Ethical

- **Amazon's Terms of Service**: Scraping may violate Amazon's ToS
- **Robots.txt**: Amazon restricts automated crawlers
- **Legal Risk**: Unauthorized scraping can have legal consequences
- **Ethical Use**: Only scrape data you have the right to access

### Best Practices

- Respect rate limits (don't send requests too fast)
- Don't overload Amazon's servers
- Consider using official APIs when available
- Check local laws regarding web scraping

### Alternatives to Scraping

1. **Amazon Product Advertising API** - Official but limited
2. **Keepa** - Historical price and image data
3. **CamelCamelCamel** - Price tracking with images
4. **Manual Download** - For small product lists
5. **Contact Amazon** - For bulk data access

## 🐛 Troubleshooting

### Problem: "403 Forbidden" Error

**Cause**: Amazon blocked your IP for automated scraping

**Solutions**:
1. Increase `--rate-limit` to 5-10 seconds
2. Wait 24-48 hours before trying again
3. Use a VPN or proxy service
4. Try the Selenium version (slower, less detectable)

### Problem: No Images Downloaded

**Cause**: Page structure changed or IP is blocked

**Solutions**:
1. Check `scraper.log` for detailed errors
2. Test accessing Amazon manually in browser
3. Try the Selenium version
4. Increase rate limit and retry

### Problem: "Module not found" Error

**Cause**: Required Python packages not installed

**Solution**:
```bash
pip install requests beautifulsoup4 pillow selenium webdriver-manager
```

### Problem: Slow Download Speed

**Cause**: High rate limit or network issues

**Solutions**:
1. Decrease `--rate-limit` (but risk IP block)
2. Check internet connection
3. Run during off-peak hours
4. Use batch processing

For more detailed troubleshooting, see `SCRAPER_GUIDE.md`

## 📋 File Structure

```
.
├── amazon_product_scraper.py          # Main scraper
├── amazon_product_scraper_selenium.py # Advanced scraper
├── batch_scraper.py                   # Batch processor
├── products-simple.json               # Your product data (108 products)
├── README.md                          # This file
├── QUICK_START.md                     # Quick start guide
├── SCRAPER_GUIDE.md                   # Comprehensive guide
│
├── product_media/                     # Downloaded images (created by scraper)
│   ├── B09XS7JWHH/
│   ├── B0CHWRXH8B/
│   └── ...
│
├── scraper.log                        # Detailed log file
└── scrape_report.json                 # Summary report
```

## 📊 Output Report

After scraping, `scrape_report.json` contains:

```json
{
  "timestamp": "2025-10-31T12:34:56.789123",
  "total_products": 108,
  "total_images_downloaded": 342,
  "total_videos_downloaded": 12,
  "total_errors": 5,
  "success_rate": "98.1%",
  "products": [
    {
      "name": "Product Name",
      "asin": "B09XS7JWHH",
      "url": "https://www.amazon.com/dp/B09XS7JWHH",
      "images_downloaded": 4,
      "videos_downloaded": 1,
      "errors": []
    }
  ]
}
```

## 🔍 What Gets Downloaded

### Images
- Main product image
- All thumbnail images
- High-resolution variants (up to 1500x1500)
- Multiple product angles/colors

### Videos
- Product demonstration videos
- Customer review videos (if available)
- 360° view videos

### Metadata
- Product name, ASIN, price
- Rating and review count
- Download timestamp
- File counts

## 💡 Advanced Usage

### Custom Rate Limiting

```bash
# Very slow (safest)
python amazon_product_scraper.py products-simple.json --rate-limit 10.0

# Medium (balanced)
python amazon_product_scraper.py products-simple.json --rate-limit 3.0

# Fast (risky)
python amazon_product_scraper.py products-simple.json --rate-limit 1.0
```

### Batch Processing with Custom Sizes

```bash
# Smaller batches (safer)
python batch_scraper.py products-simple.json --batch-size 10

# Larger batches (faster)
python batch_scraper.py products-simple.json --batch-size 50
```

### Combining Strategies

```bash
# First pass: quick scrape with basic scraper
python amazon_product_scraper.py products-simple.json

# Second pass: use Selenium for products with missing images
python amazon_product_scraper_selenium.py products-simple.json --output-dir premium_media
```

## 📞 Support & Help

1. **Check the Logs**: Review `scraper.log` for detailed error messages
2. **Read the Guide**: See `SCRAPER_GUIDE.md` for comprehensive documentation
3. **Test Manually**: Try accessing Amazon in your browser to verify access
4. **Inspect HTML**: Use browser DevTools (F12) to understand page structure
5. **Update Script**: Amazon changes their HTML structure; you may need to update regex patterns

## 🔄 Resuming Interrupted Runs

If the scraper is interrupted:

```bash
# With batch scraper, resume from batch 3
python batch_scraper.py products-simple.json --resume-from 3

# With basic scraper, re-run the same command
# (it will skip already downloaded files via hash checking)
python amazon_product_scraper.py products-simple.json
```

## 📈 Expected Results

For 108 products, you can typically expect:

- **Images**: 300-500 images (3-5 per product on average)
- **Videos**: 10-50 videos (0-1 per product on average)
- **Success Rate**: 85-95% (some products may have no images)
- **Time**: 1-4 hours depending on rate limit and internet speed
- **Disk Space**: 500 MB - 2 GB

## 🎯 Next Steps

1. **Run the Scraper**: Start with `QUICK_START.md`
2. **Monitor Progress**: Watch `scraper.log` for real-time updates
3. **Check Results**: Review `scrape_report.json` for summary
4. **Organize Media**: Use the ASIN-based directory structure
5. **Upload to Platform**: Transfer images to your e-commerce site
6. **Backup Data**: Create copies of downloaded media

## 📝 License & Disclaimer

This tool is provided for educational purposes. Users are responsible for ensuring their use complies with Amazon's Terms of Service and applicable laws. The authors assume no liability for misuse or legal consequences resulting from this tool's use.

## 🙏 Acknowledgments

Built with:
- **requests** - HTTP library
- **BeautifulSoup4** - HTML parsing
- **Selenium** - Browser automation
- **Pillow** - Image processing

---

**Version**: 1.0  
**Last Updated**: October 31, 2025  
**Python**: 3.7+

For detailed information, see `SCRAPER_GUIDE.md`
