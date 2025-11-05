/**
 * Migration script to convert current products-simple.json to unified format
 * 
 * Usage:
 *   npx tsx scripts/migrate-to-unified-format.ts
 * 
 * This script reads products-simple.json and outputs a unified format JSON file
 * that can be used as the master list for both the website and Alexa skill.
 */

import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import type { Product } from '../src/types/product';
import type { UnifiedProduct } from '../src/types/unified-product';

// Get __dirname equivalent for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Read the current products file
const productsPath = path.join(__dirname, '..', 'products-simple.json');
const outputPath = path.join(__dirname, '..', 'unified-products-master.json');

console.log('Reading products from:', productsPath);

const productsData = JSON.parse(fs.readFileSync(productsPath, 'utf-8'));
const products: Product[] = productsData;

console.log(`Found ${products.length} products to migrate`);

/**
 * Converts a Product to UnifiedProduct format
 */
function convertToUnified(product: Product): UnifiedProduct {
  // Extract currency from URL or default to USD
  const currency = 'USD';
  
  // Create a short_name from the product name (first few words)
  const nameWords = product.name.split(' ');
  const shortName = nameWords.length > 3 
    ? nameWords.slice(0, 3).join(' ') 
    : product.name;

  // Create voice_description from description (first sentence or truncated)
  const voiceDescription = product.description.length > 100
    ? product.description.substring(0, 100) + '...'
    : product.description;

  // Use ASIN as product_id if available, otherwise generate one
  const productId = product.asin || product.name.toLowerCase().replace(/[^a-z0-9]+/g, '-');

  // Convert category to proper case
  const categoryMap: Record<string, string> = {
    'electronics': 'Electronics',
    'home': 'Home & Kitchen',
    'beauty': 'Beauty & Care',
    'fashion': 'Fashion',
    'sports': 'Sports & Fitness',
    'books': 'Books',
    'toys': 'Toys & Games',
    'garden': 'Garden & Outdoor',
    'automotive': 'Automotive',
    'office': 'Office Supplies',
  };

  const unifiedProduct: UnifiedProduct = {
    product_id: productId,
    name: product.name,
    short_name: shortName,
    description: product.description,
    voice_description: voiceDescription,
    price: product.price,
    currency: currency,
    affiliate_url: product.url, // Assuming url already contains affiliate tag
    image_url: product.image_url,
    category: categoryMap[product.category] || product.category,
    is_available: true, // Default to available, can be updated manually
    rating: product.rating,
    reviews: product.reviews,
    subcategory: product.subcategory,
    badge: product.badge,
    local_images: product.local_images,
    local_videos: product.local_videos,
    image_count: product.image_count,
    video_count: product.video_count,
  };

  return unifiedProduct;
}

// Convert all products
const unifiedProducts: UnifiedProduct[] = products.map(convertToUnified);

// Write to output file
fs.writeFileSync(
  outputPath,
  JSON.stringify(unifiedProducts, null, 2),
  'utf-8'
);

console.log(`\n✅ Migration complete!`);
console.log(`   Output written to: ${outputPath}`);
console.log(`   Total products migrated: ${unifiedProducts.length}`);
console.log(`\n📋 Next steps:`);
console.log(`   1. Review the unified-products-master.json file`);
console.log(`   2. Update any product_id, short_name, or voice_description fields as needed`);
console.log(`   3. Set is_available to false for any unavailable products`);
console.log(`   4. Upload the file to S3 or another public endpoint`);
console.log(`   5. Update VITE_PRODUCT_MASTER_LIST_URL in your .env file`);

