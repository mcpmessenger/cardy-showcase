import { useState, useEffect } from "react";
import productsData from "../../products-simple.json";
import type { Product } from "@/types/product";
import {
  getAvailableUnifiedProducts,
  unifiedProductsToProducts,
  clearProductCache,
} from "./unified-products";

// Local products fallback
export const localProducts: Product[] = productsData as Product[];

// Products array - can be populated from unified master list or local fallback
// Export for backward compatibility - use getProducts() for new code
export let products: Product[] = localProducts;

/**
 * Initialize products from unified master list if available
 * Falls back to local products if fetch fails
 */
export async function initializeProducts(): Promise<Product[]> {
  try {
    const unifiedProducts = await getAvailableUnifiedProducts();
    if (unifiedProducts.length > 0) {
      products = unifiedProductsToProducts(unifiedProducts);
      console.log(`Loaded ${products.length} products from unified master list`);
      return products;
    }
  } catch (error) {
    console.warn("Failed to load unified products, using local fallback:", error);
  }
  
  // Fallback to local products
  products = localProducts;
  return products;
}

/**
 * Get current products (from unified list or local fallback)
 */
export function getProducts(): Product[] {
  return products;
}

/**
 * Refresh products from the unified master list
 */
export async function refreshProducts(): Promise<Product[]> {
  clearProductCache();
  return initializeProducts();
}

// Auto-initialize on module load (non-blocking)
if (typeof window !== "undefined") {
  initializeProducts().catch(console.error);
}

/**
 * React hook to get products with state management
 * Ensures components re-render when products are loaded from S3
 */
export function useProducts() {
  const [productsState, setProductsState] = useState<Product[]>(localProducts);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    initializeProducts()
      .then((loadedProducts) => {
        setProductsState(loadedProducts);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Failed to load products:", error);
        setProductsState(localProducts);
        setIsLoading(false);
      });
  }, []);

  return { products: productsState, isLoading };
}

/**
 * Get featured products (products with "Best Seller", "Amazon's Choice", or "Premium Pick" badges)
 */
export function getFeaturedProducts(limit: number = 8): Product[] {
  const featuredBadges = ["Best Seller", "Amazon's Choice", "Premium Pick", "Top Rated"];
  return getProducts()
    .filter((product) => product.badge && featuredBadges.includes(product.badge))
    .slice(0, limit);
}

/**
 * Get products with photos for showcasing in carousel
 * Returns ONLY products with local_images to avoid mobile display issues
 * As we add more local images, the carousel will expand automatically
 * @param productsList Optional products array to use instead of module-level products
 */
export function getProductsWithPhotos(productsList?: Product[]): Product[] {
  const productsToUse = productsList || getProducts();
  return productsToUse.filter((product) => {
    // Only return products with local images
    return product.local_images && product.local_images.length > 0;
  });
}

/**
 * Get products by category
 * @param category Category to filter by
 * @param productsList Optional products array to use instead of module-level products
 */
export function getProductsByCategory(category: string, productsList?: Product[]): Product[] {
  const productsToUse = productsList || getProducts();
  return productsToUse.filter((product) => product.category === category);
}

/**
 * Get products by subcategory
 */
export function getProductsBySubcategory(subcategory: string): Product[] {
  return getProducts().filter((product) => product.subcategory === subcategory);
}

/**
 * Get all unique categories with product counts
 * @param productsList Optional products array to use instead of module-level products
 */
export function getCategoriesWithCounts(productsList?: Product[]): Array<{ name: string; count: number; displayName: string }> {
  const productsToUse = productsList || getProducts();
  const categoryMap = new Map<string, number>();
  
  productsToUse.forEach((product) => {
    const count = categoryMap.get(product.category) || 0;
    categoryMap.set(product.category, count + 1);
  });

  const categoryDisplayNames: Record<string, string> = {
    electronics: "Electronics",
    home: "Home & Kitchen",
    beauty: "Beauty & Care",
    fashion: "Fashion",
    sports: "Sports & Fitness",
    books: "Books",
    toys: "Toys & Games",
    garden: "Garden & Outdoor",
    automotive: "Automotive",
    office: "Office Supplies",
  };

  return Array.from(categoryMap.entries())
    .map(([category, count]) => ({
      name: category,
      count,
      displayName: categoryDisplayNames[category] || category,
    }))
    .sort((a, b) => b.count - a.count);
}

/**
 * Search products by name or description
 * @param query Search query
 * @param productsList Optional products array to use instead of module-level products
 */
export function searchProducts(query: string, productsList?: Product[]): Product[] {
  const productsToUse = productsList || getProducts();
  const lowerQuery = query.toLowerCase();
  return productsToUse.filter(
    (product) =>
      product.name.toLowerCase().includes(lowerQuery) ||
      product.description.toLowerCase().includes(lowerQuery)
  );
}

/**
 * Transform Product to Gallery4Item format
 */
export function productToGalleryItem(product: Product, index?: number): {
  id: string;
  title: string;
  description: string;
  href: string;
  image: string;
  product?: Product;
} {
  // Use local image if available, otherwise fallback to image_url
  const imageUrl = product.local_images && product.local_images.length > 0
    ? `/${product.local_images[0]}` // Images served from public folder
    : product.image_url;
    
  return {
    id: product.asin || `product-${index}`,
    title: product.name,
    description: product.description,
    href: product.url,
    image: imageUrl,
    product: product, // Include full product for image carousel
  };
}

