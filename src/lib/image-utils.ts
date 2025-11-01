/**
 * Image utility functions for product images
 * Handles Amazon image URLs, fallbacks, and optimization
 */

/**
 * Get the best available image URL for a product
 * Prioritizes local images over remote URLs
 */
export function getProductImageUrl(product: {
  image_url?: string;
  local_images?: string[];
}): string {
  // Prioritize local images if available
  if (product.local_images && product.local_images.length > 0) {
    // Return the first local image, with path adjusted for web serving
    const localPath = product.local_images[0];
    // If path starts with "product_media/", serve from public folder
    // In development/production, images should be in public/product_media/
    if (localPath.startsWith('product_media/')) {
      return `/${localPath}`;
    }
    return localPath.startsWith('/') ? localPath : `/${localPath}`;
  }
  
  // Fallback to remote image URL
  return product.image_url || '/placeholder.svg';
}

/**
 * Get optimized Amazon image URL with specific size
 * Amazon image URLs support different sizes via the SL parameter
 */
export function getAmazonImageUrl(
  originalUrl: string,
  size: 'SL75' | 'SL150' | 'SL300' | 'SL500' | 'SL750' | 'SL1000' | 'SL1500' | 'SL2000' = 'SL1500'
): string {
  // If already an Amazon URL, replace the size parameter
  if (originalUrl.includes('media-amazon.com')) {
    return originalUrl.replace(/SL\d+/, size);
  }
  return originalUrl;
}

/**
 * Get image URL with CDN optimization (if using a proxy like Cloudinary)
 */
export function getOptimizedImageUrl(url: string, width?: number, height?: number): string {
  // If using a CDN, add transformation parameters here
  // Example for Cloudinary: return `https://res.cloudinary.com/demo/image/fetch/w_${width},h_${height}/${url}`;
  return url;
}

/**
 * Validate if an image URL is accessible
 */
export async function validateImageUrl(url: string): Promise<boolean> {
  try {
    const response = await fetch(url, { method: 'HEAD', mode: 'no-cors' });
    return true; // If no error, assume accessible
  } catch {
    return false;
  }
}

/**
 * Get placeholder image based on category
 */
export function getPlaceholderImage(category?: string): string {
  // Return category-specific placeholder or generic one
  return '/placeholder.svg';
}

/**
 * Extract ASIN from Amazon URL
 */
export function extractASIN(url: string): string | null {
  const match = url.match(/\/dp\/([A-Z0-9]{10})/);
  return match ? match[1] : null;
}
