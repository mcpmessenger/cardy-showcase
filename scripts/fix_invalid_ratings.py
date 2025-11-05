"""
Fix invalid ratings in unified-products-master.json.
Resets ratings that are > 5.0 back to 0 so they can be re-fetched correctly.
"""

import json
from pathlib import Path

def fix_invalid_ratings():
    """Reset invalid ratings (>5.0) to 0."""
    project_root = Path(__file__).parent.parent
    unified_file = project_root / "unified-products-master.json"
    simple_file = project_root / "products-simple.json"
    
    # Load unified products
    with open(unified_file, 'r', encoding='utf-8') as f:
        unified_products = json.load(f)
    
    # Find and fix invalid ratings
    fixed_count = 0
    for product in unified_products:
        rating = product.get('rating', 0)
        if rating > 5.0:
            print(f"Fixing {product['product_id']}: rating {rating} -> 0")
            product['rating'] = 0
            fixed_count += 1
    
    if fixed_count > 0:
        # Save unified products
        with open(unified_file, 'w', encoding='utf-8') as f:
            json.dump(unified_products, f, indent=2)
        
        # Also fix in simple products
        with open(simple_file, 'r', encoding='utf-8') as f:
            simple_products = json.load(f)
        
        for sp in simple_products:
            rating = sp.get('rating', 0)
            if rating > 5.0:
                sp['rating'] = 0
        
        with open(simple_file, 'w', encoding='utf-8') as f:
            json.dump(simple_products, f, indent=2)
        
        print(f"\nFixed {fixed_count} invalid ratings")
    else:
        print("No invalid ratings found")

if __name__ == '__main__':
    fix_invalid_ratings()

