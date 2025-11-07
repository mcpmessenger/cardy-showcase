"""Product search tool for e-commerce."""
import copy
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests

from app.config import settings

logger = logging.getLogger(__name__)

# Cache for products
_cached_products: Optional[List[Dict[str, Any]]] = None
_cache_timestamp: Optional[datetime] = None
CACHE_DURATION = timedelta(minutes=5)


def _resolve_media_url(path: Optional[str]) -> Optional[str]:
    """Convert relative media paths from the catalog into absolute S3 URLs."""
    if not path:
        return path

    if path.startswith("http://") or path.startswith("https://"):
        return path

    base_url = settings.product_media_base_url.rstrip("/") if settings.product_media_base_url else ""
    if not base_url:
        # Nothing to resolve against – return normalized relative path
        return path.lstrip("/")

    clean_path = path.lstrip("/")
    return urljoin(f"{base_url}/", clean_path)


def _normalize_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure media fields in a product reference absolute URLs."""
    normalized = copy.deepcopy(product)

    normalized["image_url"] = _resolve_media_url(product.get("image_url"))

    if isinstance(product.get("local_images"), list):
        normalized["local_images"] = [
            _resolve_media_url(image) for image in product["local_images"]
        ]

    if isinstance(product.get("local_videos"), list):
        normalized["local_videos"] = [
            _resolve_media_url(video) for video in product["local_videos"]
        ]

    # Some catalogs may provide a thumbnail field – normalize if present
    if product.get("thumbnail_url"):
        normalized["thumbnail_url"] = _resolve_media_url(product.get("thumbnail_url"))

    return normalized


def fetch_products() -> List[Dict[str, Any]]:
    """Fetch products from S3 catalog with caching."""
    global _cached_products, _cache_timestamp

    # Check cache
    if _cached_products and _cache_timestamp:
        if datetime.now() - _cache_timestamp < CACHE_DURATION:
            logger.debug("Using cached products")
            return _cached_products

    # Fetch fresh data
    try:
        logger.info(f"Fetching products from: {settings.product_catalog_url}")
        response = requests.get(settings.product_catalog_url, timeout=10)
        response.raise_for_status()
        products = response.json()

        # Filter available products
        available = [p for p in products if p.get("is_available", False)]

        normalized_products = [_normalize_product(product) for product in available]

        # Update cache
        _cached_products = normalized_products
        _cache_timestamp = datetime.now()

        logger.info(
            "Loaded %s available products (media base: %s)",
            len(normalized_products),
            settings.product_media_base_url,
        )
        return normalized_products

    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        # Return cached data if available, even if expired
        if _cached_products:
            logger.warning("Using stale cached products")
            return _cached_products
        return []


def search_products(
    query: str, 
    max_price: Optional[float] = None, 
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search products matching criteria.
    
    Args:
        query: Search query (searches name, short_name, description)
        max_price: Optional maximum price filter
        category: Optional category filter
    
    Returns:
        List of matching products (max 5)
    """
    products = fetch_products()
    query_lower = query.lower()
    
    # Special handling for motorcycle searches
    is_motorcycle_query = "motorcycle" in query_lower or "bike" in query_lower
    
    results = []
    for product in products:
        # Search in multiple fields
        name_match = query_lower in product.get("name", "").lower()
        short_name_match = query_lower in product.get("short_name", "").lower()
        desc_match = query_lower in product.get("description", "").lower()
        voice_desc_match = query_lower in product.get("voice_description", "").lower()
        
        # Special motorcycle detection: check if "motorcycle" appears in description
        # or as 3rd word in product title when searching for motorcycles
        motorcycle_match = False
        if is_motorcycle_query:
            product_name = product.get("name", "")
            product_desc = product.get("description", "").lower()
            product_voice_desc = product.get("voice_description", "").lower()
            
            # Check if "motorcycle" appears in description
            if "motorcycle" in product_desc or "motorcycle" in product_voice_desc:
                motorcycle_match = True
            else:
                # Check if "motorcycle" is the 3rd word in the product title
                name_words = product_name.split()
                if len(name_words) >= 3 and name_words[2].lower() == "motorcycle":
                    motorcycle_match = True
        
        # Price filter
        if max_price and product.get("price", float('inf')) > max_price:
            continue
        
        # Category filter
        if category and product.get("category", "").lower() != category.lower():
            continue
        
        if name_match or short_name_match or desc_match or voice_desc_match or motorcycle_match:
            results.append(product)
    
    # Return top 5 results
    return results[:5]


def add_to_cart(product_id: str, quantity: int = 1) -> Dict[str, Any]:
    """
    Add product to cart (placeholder - implement cart storage later).
    
    Args:
        product_id: Product ID to add
        quantity: Quantity to add
    
    Returns:
        Success message
    """
    # TODO: Implement actual cart storage (database, session, etc.)
    logger.info(f"Adding {quantity}x product {product_id} to cart")
    return {
        "success": True,
        "message": f"Added {quantity} item(s) with ID {product_id} to your cart.",
        "product_id": product_id,
        "quantity": quantity
    }

