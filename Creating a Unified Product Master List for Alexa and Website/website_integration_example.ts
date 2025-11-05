// website_integration_example.ts

// --- Configuration ---
const PRODUCT_MASTER_LIST_URL = "https://your-s3-bucket-name.s3.amazonaws.com/products.json";

// --- Data Structure (for type safety in TypeScript) ---
interface Product {
    product_id: string;
    name: string;
    short_name: string;
    description: string;
    voice_description: string;
    price: number;
    currency: string;
    affiliate_url: string;
    image_url: string;
    category: string;
    rating: number;
    is_available: boolean;
}

/**
 * Fetches the product master list from the S3 endpoint.
 * @returns A promise that resolves to an array of Product objects.
 */
async function fetchProductList(): Promise<Product[]> {
    try {
        const response = await fetch(PRODUCT_MASTER_LIST_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const products: Product[] = await response.json();
        return products.filter(p => p.is_available); // Only show available products
    } catch (error) {
        console.error("Failed to fetch product list:", error);
        // Fallback: return an empty array or a cached version
        return [];
    }
}

/**
 * Renders the product list on the website.
 * @param products The array of products to display.
 */
function renderProducts(products: Product[]): void {
    const container = document.getElementById('product-list-container');
    if (!container) return;

    container.innerHTML = products.map(product => `
        <div class="product-card">
            <img src="${product.image_url}" alt="${product.name}" class="product-image">
            <h2 class="product-name">${product.name}</h2>
            <p class="product-price">${product.currency} ${product.price.toFixed(2)}</p>
            <p class="product-description">${product.description.substring(0, 100)}...</p>
            <p class="product-category">Category: ${product.category}</p>
            <a href="${product.affiliate_url}" target="_blank" class="buy-button">Buy Now (Affiliate Link)</a>
        </div>
    `).join('');
}

// --- Main execution ---
(async () => {
    const products = await fetchProductList();
    renderProducts(products);
})();

// NOTE: In a real-world application like cardy-showcase (React/Vite), 
// you would integrate this logic into a React component's lifecycle (e.g., useEffect).
// The core logic of fetching from the URL remains the same.
