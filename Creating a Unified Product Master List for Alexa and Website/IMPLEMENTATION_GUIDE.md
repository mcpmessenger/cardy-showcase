# Unified Product Master List - Implementation Guide

This guide explains how the unified product master list system has been integrated into your project.

## Overview

The unified product master list allows both your website (tubbyai.com) and your Alexa skill (Alicia) to share the same product data from a single source of truth. The system automatically fetches products from a public endpoint and falls back to local products if the fetch fails.

## Architecture

```
┌─────────────────────────────────┐
│  Public Endpoint (S3/GitHub)   │
│  unified-products-master.json  │
└──────────────┬──────────────────┘
               │
               │ HTTP GET
               ▼
┌─────────────────────────────────┐
│   src/lib/unified-products.ts   │
│   - Fetches & caches products   │
│   - Converts to Product format  │
└──────────────┬──────────────────┘
               │
               │
┌──────────────▼──────────────────┐
│      src/lib/products.ts        │
│   - Uses unified products       │
│   - Falls back to local JSON    │
│   - All existing functions work │
└─────────────────────────────────┘
```

## Files Created

### 1. `src/types/unified-product.ts`
- Defines the `UnifiedProduct` interface matching the master list schema
- Includes voice-friendly fields like `short_name` and `voice_description`

### 2. `src/lib/unified-products.ts`
- Fetches products from the public endpoint
- Implements caching (5-minute cache duration)
- Provides search and filtering functions
- Converts unified format to current Product format for backward compatibility

### 3. `scripts/migrate-to-unified-format.ts`
- Migration script to convert `products-simple.json` to unified format
- Run with: `npx tsx scripts/migrate-to-unified-format.ts`

### 4. Updated `src/lib/products.ts`
- Now supports both unified and local products
- Automatically initializes from unified master list on page load
- Falls back to local products if fetch fails
- All existing functions continue to work

## Setup Instructions

### Step 1: Generate Unified Format

Run the migration script to convert your current products:

```bash
npx tsx scripts/migrate-to-unified-format.ts
```

This creates `unified-products-master.json` in your project root.

### Step 2: Review and Edit

Open `unified-products-master.json` and:
- Review `short_name` fields (voice-friendly names)
- Review `voice_description` fields (natural-sounding descriptions)
- Set `is_available: false` for unavailable products
- Verify `affiliate_url` contains your affiliate tag

### Step 3: Upload to Public Endpoint

Upload the JSON file to one of these options:

#### Option A: AWS S3 (Recommended)
1. Create an S3 bucket (or use existing)
2. Upload `unified-products-master.json`
3. Make it publicly readable
4. Get the public URL (e.g., `https://your-bucket.s3.amazonaws.com/unified-products-master.json`)

#### Option B: GitHub Gist
1. Create a new Gist
2. Paste the JSON content
3. Get the raw URL (e.g., `https://gist.githubusercontent.com/username/gist-id/raw/unified-products-master.json`)

#### Option C: Your Own Server
- Host the file on any public web server
- Ensure CORS headers allow access from your domain

### Step 4: Configure Environment Variable

Create or update your `.env` file:

```env
VITE_PRODUCT_MASTER_LIST_URL=https://your-bucket.s3.amazonaws.com/unified-products-master.json
```

Or set it in your deployment configuration (Vercel, Netlify, etc.).

### Step 5: Test

1. Start your development server
2. Check the browser console for: `"Loaded X products from unified master list"`
3. If you see a warning about fallback, check the URL and CORS settings

## Usage

### In Your Website Code

The existing product functions work automatically:

```typescript
import { getProducts, getFeaturedProducts, searchProducts } from '@/lib/products';

// These automatically use unified products if available
const products = getProducts();
const featured = getFeaturedProducts(8);
const searchResults = searchProducts('headphones');
```

### Manual Refresh

If you need to refresh products without reloading:

```typescript
import { refreshProducts } from '@/lib/products';

await refreshProducts();
```

### Direct Unified Product Access

For Alexa-specific features (voice descriptions, etc.):

```typescript
import { 
  fetchUnifiedProductList, 
  searchUnifiedProducts 
} from '@/lib/unified-products';

const unifiedProducts = await fetchUnifiedProductList();
const voiceResults = await searchUnifiedProducts('smart feeder');
```

## For Alexa Skill Integration

Use the Python example from `alexa_integration_example.py` in your Lambda function. The Python code fetches from the same URL as the website.

## Benefits

1. **Single Source of Truth**: Update products once, both systems get updates
2. **Real-time Updates**: No code deployments needed to update products
3. **Backward Compatible**: Existing code continues to work
4. **Graceful Fallback**: If the endpoint is unavailable, local products are used
5. **Caching**: Products are cached for 5 minutes to reduce API calls

## Troubleshooting

### Products not loading from unified list

1. Check browser console for errors
2. Verify the URL in `VITE_PRODUCT_MASTER_LIST_URL`
3. Test the URL directly in a browser
4. Check CORS headers on the endpoint
5. Verify the JSON is valid

### Products stuck on old data

- The cache lasts 5 minutes
- Call `refreshProducts()` to force refresh
- Or clear browser cache

### Migration script errors

- Ensure `products-simple.json` exists in project root
- Check that TypeScript/tsx is installed: `npm install -D tsx`
- Run with: `npx tsx scripts/migrate-to-unified-format.ts`

## Next Steps

1. ✅ Migration script created
2. ✅ Unified product types created
3. ✅ Fetching utilities implemented
4. ✅ Backward compatibility maintained
5. ⏳ Run migration script
6. ⏳ Upload to public endpoint
7. ⏳ Configure environment variable
8. ⏳ Test integration
9. ⏳ Update Alexa Lambda function to use the same URL

