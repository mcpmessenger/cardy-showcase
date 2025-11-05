# alexa_integration_example.py

import json
import requests
from typing import List, Dict, Any

# --- Configuration ---
PRODUCT_MASTER_LIST_URL = "https://your-s3-bucket-name.s3.amazonaws.com/products.json"

# --- Data Structure (for type hinting) ---
Product = Dict[str, Any]

def fetch_product_list() -> List[Product]:
    """
    Fetches the product master list from the S3 endpoint.
    In a production Lambda, you might want to cache this response.
    """
    try:
        response = requests.get(PRODUCT_MASTER_LIST_URL, timeout=5)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        products: List[Product] = response.json()
        return [p for p in products if p.get("is_available", False)] # Filter for available products
    except requests.exceptions.RequestException as e:
        print(f"Error fetching product list: {e}")
        # Fallback: return an empty list or a hardcoded list of popular products
        return []

def find_product_by_name(products: List[Product], search_term: str) -> Product | None:
    """
    Searches for a product by name or short name, case-insensitively.
    """
    search_term_lower = search_term.lower()
    for product in products:
        name_lower = product.get("name", "").lower()
        short_name_lower = product.get("short_name", "").lower()
        
        if search_term_lower in name_lower or search_term_lower in short_name_lower:
            return product
    return None

def generate_alexa_response(product: Product) -> str:
    """
    Generates a simple Alexa voice response for a found product.
    In a real skill, this would involve generating SSML and APL directives.
    """
    name = product["name"]
    voice_desc = product["voice_description"]
    price = product["price"]
    currency = product["currency"]
    affiliate_url = product["affiliate_url"]
    
    speech_text = (
        f"I found the {name}. {voice_desc}. "
        f"It costs {currency} {price:.2f}. "
        f"I can send the affiliate link to your Alexa app. Would you like me to do that?"
    )
    
    # In a real Alexa skill, you would also add a Card or APL directive
    # with the image_url and affiliate_url.
    
    return speech_text

# --- Example Usage in a Lambda Handler ---
def lambda_handler(event, context):
    # 1. Fetch the unified product list
    product_list = fetch_product_list()
    
    if not product_list:
        return "Sorry, I'm having trouble accessing the product catalog right now."

    # 2. Get the user's request (e.g., product name from an intent slot)
    # For this example, we'll hardcode a search term
    user_search_term = "smart collar" 
    
    # 3. Find the product
    found_product = find_product_by_name(product_list, user_search_term)
    
    if found_product:
        # 4. Generate the response
        response = generate_alexa_response(found_product)
        print(f"Alexa Speech: {response}")
        return response
    else:
        return f"Sorry, I couldn't find any product matching '{user_search_term}'."

# To test locally:
if __name__ == "__main__":
    print("--- Testing Alexa Integration Example ---")
    result = lambda_handler(None, None)
    print(f"\nFinal Result: {result}")
