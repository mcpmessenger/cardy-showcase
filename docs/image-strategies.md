# Programmatic Product Image Strategy

## Current Situation
- You have 84 products with Amazon image URLs (`image_url` field)
- Images are hosted on `m.media-amazon.com`
- Format: `https://m.media-amazon.com/images/I/[IMAGE_ID]._AC_SL1500_.jpg`

## Strategy Options

### 1. **Amazon Product Advertising API (PA-API)**
**Best for:** Official, reliable, high-quality images

**Pros:**
- Official Amazon API
- Guaranteed image availability
- Multiple image sizes available
- Includes product metadata

**Cons:**
- Requires Amazon Associate account
- API keys needed
- Rate limits apply
- Costs may apply for high volume

**Implementation:**
```javascript
// Using amazon-product-api or similar
const api = require('amazon-product-api');
const client = api.createClient({
  awsId: "YOUR_ACCESS_KEY",
  awsSecret: "YOUR_SECRET_KEY",
  awsTag: "aipro00-20"
});

// Fetch product images by ASIN
async function getProductImages(asin) {
  const response = await client.itemLookup({
    idType: 'ASIN',
    itemId: asin,
    responseGroup: 'Images'
  });
  return response[0].LargeImage[0].URL[0];
}
```

---

### 2. **Amazon Image URL Pattern (Current Approach)**
**Best for:** Quick, no API needed, works with existing ASINs

**Pros:**
- No API keys required
- Simple URL pattern
- Works with existing ASINs
- Different sizes available via URL parameters

**Cons:**
- URLs may break if Amazon changes structure
- No guarantee of image availability
- Limited metadata

**Implementation:**
```javascript
// Extract image ID from existing URLs or construct from ASIN
function getAmazonImageUrl(asin, size = 'SL1500') {
  // Option 1: Scrape from product page
  // Option 2: Use existing image_url if available
  // Option 3: Construct from known patterns
  return `https://m.media-amazon.com/images/I/[IMAGE_ID]._AC_${size}_.jpg`;
}

// Different sizes available:
// SL75, SL150, SL300, SL500, SL750, SL1000, SL1500, SL2000
```

---

### 3. **Image Download & CDN Strategy**
**Best for:** Performance, reliability, control

**Pros:**
- Faster loading (your CDN)
- No dependency on Amazon
- Can optimize images
- Better SEO/caching

**Cons:**
- Storage costs
- Initial download time
- Maintenance overhead

**Implementation:**
```javascript
// Download and optimize images
const sharp = require('sharp');
const axios = require('axios');
const fs = require('fs');

async function downloadAndOptimize(product) {
  const response = await axios.get(product.image_url, {
    responseType: 'arraybuffer'
  });
  
  // Optimize with Sharp
  const optimized = await sharp(response.data)
    .resize(800, 800, { fit: 'inside', withoutEnlargement: true })
    .jpeg({ quality: 85 })
    .toBuffer();
  
  // Upload to CDN (Cloudinary, Imgix, etc.)
  // Save reference in your database
  return cdnUrl;
}
```

---

### 4. **Unsplash/Stock Photo API** (For Placeholders)
**Best for:** Fallback images, category placeholders

**Pros:**
- Free tier available
- High quality
- Good for placeholders

**Cons:**
- Not product-specific
- Generic images

**Implementation:**
```javascript
const Unsplash = require('unsplash-js');
const unsplash = new Unsplash({ accessKey: 'YOUR_KEY' });

async function getCategoryPlaceholder(category) {
  const searchTerms = {
    electronics: 'electronics gadgets',
    home: 'home decor',
    fashion: 'fashion style',
    // etc.
  };
  
  const photos = await unsplash.search.photos(searchTerms[category], 1);
  return photos.results[0].urls.regular;
}
```

---

### 5. **Web Scraping (Last Resort)**
**Best for:** When APIs aren't available

**Pros:**
- Works with any website
- Can extract multiple images

**Cons:**
- May violate ToS
- Fragile (breaks on site changes)
- Legal/ethical concerns

**Implementation:**
```javascript
const puppeteer = require('puppeteer');
const cheerio = require('cheerio');

async function scrapeAmazonImages(asin) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto(`https://www.amazon.com/dp/${asin}`);
  
  const images = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('#main-image, #altImages img'))
      .map(img => img.src)
      .filter(src => src.includes('media-amazon.com'));
  });
  
  await browser.close();
  return images;
}
```

---

## Recommended Approach for Your Store

### **Hybrid Strategy:**

1. **Primary:** Keep using Amazon image URLs (you already have them)
2. **Fallback:** Download to your CDN for critical products
3. **Optimization:** Add image optimization service

### Implementation Steps:

1. **Validate existing images:**
   ```javascript
   // Check which images are still valid
   async function validateImageUrls(products) {
     const results = await Promise.allSettled(
       products.map(async (product) => {
         const response = await fetch(product.image_url, { method: 'HEAD' });
         return {
           asin: product.asin,
           valid: response.ok,
           status: response.status
         };
       })
     );
     return results;
   }
   ```

2. **Add image optimization proxy:**
   ```javascript
   // Use a service like Cloudinary or Imgix as proxy
   // This automatically optimizes on-the-fly
   function getOptimizedImageUrl(originalUrl, width = 800) {
     return `https://res.cloudinary.com/your-cloud/image/fetch/w_${width},q_auto,f_auto/${encodeURIComponent(originalUrl)}`;
   }
   ```

3. **Implement lazy loading:**
   ```jsx
   // Already using React - add lazy loading
   <img
     src={product.image_url}
     loading="lazy"
     alt={product.name}
     onError={(e) => {
       // Fallback to placeholder
       e.target.src = '/placeholder.svg';
     }}
   />
   ```

---

## Quick Win: Image Validation Script

Create a script to validate all your current image URLs:

```javascript
// scripts/validate-images.js
import products from '../products-simple.json';

async function validateAllImages() {
  const results = [];
  
  for (const product of products) {
    try {
      const response = await fetch(product.image_url, { method: 'HEAD' });
      results.push({
        asin: product.asin,
        name: product.name,
        valid: response.ok,
        status: response.status
      });
    } catch (error) {
      results.push({
        asin: product.asin,
        name: product.name,
        valid: false,
        error: error.message
      });
    }
    
    // Rate limiting
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  const valid = results.filter(r => r.valid).length;
  const invalid = results.filter(r => !r.valid);
  
  console.log(`Valid: ${valid}/${results.length}`);
  console.log('Invalid images:', invalid);
  
  return results;
}
```

---

## Best Practices

1. **Always have fallbacks** - Don't break the UI if an image fails
2. **Use appropriate sizes** - Don't load 2000px images for thumbnails
3. **Implement lazy loading** - Better performance
4. **Cache images** - Use CDN with proper cache headers
5. **Monitor image health** - Periodically check if URLs are still valid
6. **Optimize formats** - Use WebP where supported, fallback to JPEG

---

## Recommendation

**For your current setup:**
1. ✅ Keep using Amazon URLs (they work, you have them)
2. Add image error handling with fallbacks
3. Consider a CDN proxy for optimization (Cloudinary free tier works well)
4. Implement lazy loading (already supported in modern browsers)
5. Monitor periodically for broken links

**Future scaling:**
- If images become unreliable, migrate to your own CDN
- Use Amazon PA-API if you need official access
- Consider image optimization service for better performance

