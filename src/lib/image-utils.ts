/**
 * Image utility functions for product images
 * Handles Amazon image URLs, fallbacks, and optimization
 */

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
export function getOptimizedImageUrl(
  originalUrl: string,
  options?: {
    width?: number;
    height?: number;
    quality?: number;
    format?: 'auto' | 'webp' | 'jpeg' | 'png';
  }
): string {
  const { width = 800, height, quality = 85, format = 'auto' } = options || {};

  // Example: Using Cloudinary or Imgix as proxy
  // Replace with your actual CDN/proxy service
  const useCDN = false; // Set to true when you have a CDN setup

  if (useCDN) {
    // Cloudinary example
    // return `https://res.cloudinary.com/YOUR_CLOUD/image/fetch/w_${width},q_${quality},f_${format}/${encodeURIComponent(originalUrl)}`;
    
    // Imgix example
    // return `https://your-domain.imgix.net/${encodeURIComponent(originalUrl)}?w=${width}&q=${quality}&auto=format`;
  }

  return originalUrl;
}

/**
 * Validate if an image URL is accessible
 */
export async function validateImageUrl(url: string): Promise<boolean> {
  try {
    const response = await fetch(url, { method: 'HEAD', mode: 'no-cors' });
    // With no-cors, we can't check status, so we'll just return true
    // For proper validation, you'd need a backend endpoint
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Get fallback/placeholder image URL
 */
export function getPlaceholderImage(category?: string): string {
  // Use a placeholder service like Unsplash, Placeholder.com, or your own
  const placeholderServices = {
    placeholder: 'https://via.placeholder.com/800x800/cccccc/666666?text=Product+Image',
    placeholderSvg: '/placeholder.svg', // Your local placeholder
    unsplash: category 
      ? `https://source.unsplash.com/800x800/?${encodeURIComponent(category)}`
      : 'https://source.unsplash.com/800x800/?product',
  };

  return placeholderServices.placeholderSvg; // Use local placeholder
}

/**
 * Extract ASIN from Amazon URL
 */
export function extractASIN(url: string): string | null {
  // Extract ASIN from various Amazon URL formats
  const patterns = [
    /\/dp\/([A-Z0-9]{10})/,           // /dp/B09XS7JWHH
    /\/gp\/product\/([A-Z0-9]{10})/,   // /gp/product/B09XS7JWHH
    /\/product\/([A-Z0-9]{10})/,       // /product/B09XS7JWHH
  ];

  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) return match[1];
  }

  return null;
}

/**
 * Get multiple image sizes for responsive images
 */
export function getResponsiveImageUrls(
  originalUrl: string,
  sizes: number[] = [400, 800, 1200]
): { src: string; srcSet: string; sizes: string } {
  const srcSet = sizes
    .map((size) => {
      const url = getOptimizedImageUrl(originalUrl, { width: size });
      return `${url} ${size}w`;
    })
    .join(', ');

  return {
    src: getOptimizedImageUrl(originalUrl, { width: sizes[0] }),
    srcSet,
    sizes: '(max-width: 400px) 400px, (max-width: 800px) 800px, 1200px',
  };
}

