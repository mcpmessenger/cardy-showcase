import productsData from "../../products-simple.json";
import type { Product } from "@/types/product";

export const products: Product[] = productsData as Product[];

/**
 * Get featured products (products with "Best Seller", "Amazon's Choice", or "Premium Pick" badges)
 */
export function getFeaturedProducts(limit: number = 8): Product[] {
  const featuredBadges = ["Best Seller", "Amazon's Choice", "Premium Pick", "Top Rated"];
  return products
    .filter((product) => product.badge && featuredBadges.includes(product.badge))
    .slice(0, limit);
}

/**
 * Get products with photos for showcasing in carousel
 * Returns ONLY products with local_images to avoid mobile display issues
 * As we add more local images, the carousel will expand automatically
 */
export function getProductsWithPhotos(): Product[] {
  return products.filter((product) => {
    // Only return products with local images
    return product.local_images && product.local_images.length > 0;
  });
}

/**
 * Get products by category
 */
export function getProductsByCategory(category: string): Product[] {
  return products.filter((product) => product.category === category);
}

/**
 * Get products by subcategory
 */
export function getProductsBySubcategory(subcategory: string): Product[] {
  return products.filter((product) => product.subcategory === subcategory);
}

/**
 * Get all unique categories with product counts
 */
export function getCategoriesWithCounts(): Array<{ name: string; count: number; displayName: string }> {
  const categoryMap = new Map<string, number>();
  
  products.forEach((product) => {
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
 */
export function searchProducts(query: string): Product[] {
  const lowerQuery = query.toLowerCase();
  return products.filter(
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

