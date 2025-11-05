import type { UnifiedProduct } from "@/types/unified-product";
import type { Product } from "@/types/product";

/**
 * Configuration for the unified product master list
 * Update this URL when you deploy the master list to S3 or another public endpoint
 */
export const PRODUCT_MASTER_LIST_URL = 
  import.meta.env.VITE_PRODUCT_MASTER_LIST_URL || 
  "https://your-s3-bucket-name.s3.amazonaws.com/products.json";

/**
 * Cache for the product list to avoid repeated fetches
 */
let cachedProducts: UnifiedProduct[] | null = null;
let cacheTimestamp: number = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

/**
 * Fetches the unified product master list from the public endpoint
 * @returns A promise that resolves to an array of UnifiedProduct objects
 */
export async function fetchUnifiedProductList(): Promise<UnifiedProduct[]> {
  // Return cached data if still valid
  const now = Date.now();
  if (cachedProducts && (now - cacheTimestamp) < CACHE_DURATION) {
    return cachedProducts;
  }

  try {
    const response = await fetch(PRODUCT_MASTER_LIST_URL, {
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const products: UnifiedProduct[] = await response.json();
    
    // Validate that we received an array
    if (!Array.isArray(products)) {
      throw new Error("Invalid product list format: expected an array");
    }

    // Cache the results
    cachedProducts = products;
    cacheTimestamp = now;

    return products;
  } catch (error) {
    console.error("Failed to fetch unified product list:", error);
    
    // Return cached data if available, even if expired
    if (cachedProducts) {
      console.warn("Using stale cached product data");
      return cachedProducts;
    }

    // Fallback: return empty array
    return [];
  }
}

/**
 * Gets only available products from the unified master list
 */
export async function getAvailableUnifiedProducts(): Promise<UnifiedProduct[]> {
  const products = await fetchUnifiedProductList();
  return products.filter((product) => product.is_available);
}

/**
 * Finds a product by ID in the unified master list
 */
export async function findUnifiedProductById(productId: string): Promise<UnifiedProduct | null> {
  const products = await fetchUnifiedProductList();
  return products.find((p) => p.product_id === productId) || null;
}

/**
 * Searches products in the unified master list by name or short_name
 */
export async function searchUnifiedProducts(query: string): Promise<UnifiedProduct[]> {
  const products = await getAvailableUnifiedProducts();
  const lowerQuery = query.toLowerCase();

  return products.filter((product) => {
    const nameMatch = product.name.toLowerCase().includes(lowerQuery);
    const shortNameMatch = product.short_name?.toLowerCase().includes(lowerQuery);
    const descriptionMatch = product.description.toLowerCase().includes(lowerQuery);
    const voiceDescriptionMatch = product.voice_description?.toLowerCase().includes(lowerQuery);

    return nameMatch || shortNameMatch || descriptionMatch || voiceDescriptionMatch;
  });
}

/**
 * Gets products by category from the unified master list
 */
export async function getUnifiedProductsByCategory(category: string): Promise<UnifiedProduct[]> {
  const products = await getAvailableUnifiedProducts();
  return products.filter((product) => 
    product.category.toLowerCase() === category.toLowerCase()
  );
}

/**
 * Converts a UnifiedProduct to the current Product format for backward compatibility
 */
export function unifiedProductToProduct(unified: UnifiedProduct): Product {
  // Extract ASIN from product_id or affiliate_url if possible
  let asin = unified.product_id;
  
  // Try to extract ASIN from affiliate_url if it contains /dp/ or /gp/
  const asinMatch = unified.affiliate_url.match(/\/dp\/([A-Z0-9]{10})|\/gp\/product\/([A-Z0-9]{10})/);
  if (asinMatch) {
    asin = asinMatch[1] || asinMatch[2];
  }

  return {
    name: unified.name,
    price: unified.price,
    asin: asin,
    url: unified.affiliate_url,
    image_url: unified.image_url,
    rating: unified.rating || 0,
    reviews: unified.reviews || 0,
    description: unified.description,
    category: unified.category.toLowerCase(),
    subcategory: unified.subcategory || unified.category.toLowerCase(),
    badge: unified.badge,
    local_images: unified.local_images,
    local_videos: unified.local_videos,
    image_count: unified.image_count || unified.local_images?.length || 0,
    video_count: unified.video_count || unified.local_videos?.length || 0,
  };
}

/**
 * Converts an array of UnifiedProducts to Products
 */
export function unifiedProductsToProducts(unified: UnifiedProduct[]): Product[] {
  return unified.map(unifiedProductToProduct);
}

/**
 * Clears the product cache (useful for testing or forcing a refresh)
 */
export function clearProductCache(): void {
  cachedProducts = null;
  cacheTimestamp = 0;
}

