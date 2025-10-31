/**
 * Image validation script
 * Checks if all product image URLs are still accessible
 * 
 * Usage: node scripts/validate-images.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function validateImageUrl(url) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

    const response = await fetch(url, {
      method: 'HEAD',
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    return {
      valid: response.ok,
      status: response.status,
    };
  } catch (error) {
    return {
      valid: false,
      error: error.message,
    };
  }
}

async function validateAllImages() {
  const productsPath = path.join(__dirname, '..', 'products-simple.json');
  const products = JSON.parse(fs.readFileSync(productsPath, 'utf-8'));

  console.log(`Validating ${products.length} product images...\n`);

  const results = [];
  let validCount = 0;
  let invalidCount = 0;

  for (let i = 0; i < products.length; i++) {
    const product = products[i];
    const result = await validateImageUrl(product.image_url);

    const status = {
      index: i + 1,
      asin: product.asin,
      name: product.name.substring(0, 50) + '...',
      url: product.image_url,
      ...result,
    };

    results.push(status);

    if (result.valid) {
      validCount++;
      process.stdout.write(`✓ ${i + 1}/${products.length}\r`);
    } else {
      invalidCount++;
      console.log(`\n✗ [${i + 1}] ${product.asin} - ${product.name.substring(0, 50)}`);
      console.log(`  URL: ${product.image_url}`);
      console.log(`  Error: ${result.error || `Status ${result.status}`}\n`);
    }

    // Rate limiting - wait 100ms between requests
    if (i < products.length - 1) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log(`Validation Complete:`);
  console.log(`  Valid: ${validCount}/${products.length} (${((validCount / products.length) * 100).toFixed(1)}%)`);
  console.log(`  Invalid: ${invalidCount}/${products.length} (${((invalidCount / products.length) * 100).toFixed(1)}%)`);
  console.log('='.repeat(60));

  // Save results to file
  const resultsPath = path.join(__dirname, '..', 'image-validation-results.json');
  fs.writeFileSync(
    resultsPath,
    JSON.stringify(results, null, 2),
    'utf-8'
  );
  console.log(`\nResults saved to: ${resultsPath}`);

  return results;
}

// Run validation
validateAllImages().catch(console.error);

