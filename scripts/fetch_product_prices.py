"""
Script to fetch product prices, ratings, and reviews from Amazon product pages.
Updates the unified-products-master.json and products-simple.json files with actual data.
"""

import json
import re
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def extract_price_from_page(driver, url: str) -> float:
    """Extract price from Amazon product page."""
    try:
        driver.get(url)
        time.sleep(3)
        
        # Try to accept cookies
        try:
            consent = driver.find_element(By.ID, "sp-cc-accept")
            consent.click()
            time.sleep(1)
        except:
            pass
        
        # Multiple price selectors
        price_selectors = [
            (By.ID, "priceblock_ourprice"),
            (By.ID, "priceblock_dealprice"),
            (By.ID, "priceblock_saleprice"),
            (By.CSS_SELECTOR, ".a-price .a-offscreen"),
            (By.CSS_SELECTOR, ".a-price-whole"),
            (By.CSS_SELECTOR, "span.a-price[data-a-color='base'] span.a-offscreen"),
            (By.CSS_SELECTOR, "span[data-a-color='price'] .a-offscreen"),
        ]
        
        for by, selector in price_selectors:
            try:
                element = driver.find_element(by, selector)
                price_text = element.text or element.get_attribute("textContent")
                if price_text:
                    # Extract numeric price
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        price = float(price_match.group().replace(',', ''))
                        return price
            except:
                continue
        
        # Try to extract from page source
        page_source = driver.page_source
        price_patterns = [
            r'"priceAmount":(\d+\.?\d*)',
            r'"displayPrice":"\$([\d,]+\.?\d*)"',
            r'"buyingPrice":(\d+\.?\d*)',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, page_source)
            if match:
                try:
                    price = float(match.group(1).replace(',', ''))
                    return price
                except:
                    continue
        
        return 0.0
    except Exception as e:
        print(f"    Error extracting price: {e}")
        return 0.0

def extract_rating_and_reviews_from_page(driver, url: str) -> tuple:
    """Extract rating and review count from Amazon product page."""
    try:
        driver.get(url)
        time.sleep(3)
        
        # Try to accept cookies
        try:
            consent = driver.find_element(By.ID, "sp-cc-accept")
            consent.click()
            time.sleep(1)
        except:
            pass
        
        rating = 0.0
        reviews = 0
        
        # Try to find rating element (star rating should be 1.0-5.0)
        rating_selectors = [
            (By.ID, "acrPopover"),
            (By.CSS_SELECTOR, "span[data-hook='rating-out-of-text']"),
            (By.CSS_SELECTOR, "span.a-icon-alt"),
            (By.CSS_SELECTOR, "i.a-icon-star"),
            (By.CSS_SELECTOR, "#acrPopover"),
        ]
        
        for by, selector in rating_selectors:
            try:
                element = driver.find_element(by, selector)
                text = element.text or element.get_attribute("textContent") or element.get_attribute("aria-label") or ""
                
                if text:
                    # Extract rating - must be between 1.0 and 5.0
                    rating_match = re.search(r'(\d\.\d+)\s*out\s*of\s*5|(\d\.\d+)\s*stars?|(\d\.\d+)(?=\s*out)', text)
                    if rating_match:
                        rating_str = rating_match.group(1) or rating_match.group(2) or rating_match.group(3)
                        rating_val = float(rating_str)
                        # Only accept valid ratings (1.0-5.0)
                        if 1.0 <= rating_val <= 5.0:
                            rating = rating_val
            except:
                continue
        
        # Try to find review count separately
        review_selectors = [
            (By.ID, "acrCustomerReviewText"),
            (By.CSS_SELECTOR, "a[data-hook='see-all-reviews-link-foot']"),
            (By.CSS_SELECTOR, "#acrCustomerReviewLink"),
            (By.CSS_SELECTOR, "span[data-hook='total-review-count']"),
        ]
        
        for by, selector in review_selectors:
            try:
                element = driver.find_element(by, selector)
                text = element.text or element.get_attribute("textContent") or ""
                
                if text:
                    # Extract review count
                    review_match = re.search(r'([\d,]+)\s*(?:ratings?|reviews?)', text, re.IGNORECASE)
                    if review_match:
                        reviews_str = review_match.group(1).replace(',', '')
                        reviews = int(reviews_str)
                        if reviews > 0:
                            break
            except:
                continue
        
        # Try to extract from page source/JSON data
        if rating == 0 or reviews == 0:
            page_source = driver.page_source
            
            # Look for rating in JSON data (must be 1.0-5.0)
            rating_patterns = [
                r'"averageRating":(\d\.\d+)',
                r'"ratingValue":(\d\.\d+)',
                r'"rating":(\d\.\d+)',
                r'"starRating":(\d\.\d+)',
            ]
            
            for pattern in rating_patterns:
                match = re.search(pattern, page_source)
                if match:
                    try:
                        rating_val = float(match.group(1))
                        # Only accept valid ratings (1.0-5.0)
                        if 1.0 <= rating_val <= 5.0:
                            rating = rating_val
                            break
                    except:
                        continue
            
            # Look for review count in JSON data
            review_patterns = [
                r'"reviewCount":(\d+)',
                r'"totalReviews":(\d+)',
                r'"ratingCount":(\d+)',
            ]
            
            for pattern in review_patterns:
                match = re.search(pattern, page_source)
                if match:
                    try:
                        reviews = int(match.group(1))
                        break
                    except:
                        continue
        
        return rating, reviews
    except Exception as e:
        print(f"    Error extracting rating/reviews: {e}")
        return 0.0, 0

def update_product_data():
    """Update prices, ratings, and reviews for products with missing data."""
    project_root = Path(__file__).parent.parent
    unified_file = project_root / "unified-products-master.json"
    simple_file = project_root / "products-simple.json"
    
    # Load unified products
    with open(unified_file, 'r', encoding='utf-8') as f:
        unified_products = json.load(f)
    
    # Find products with missing data (price, rating, or reviews)
    products_needing_data = [
        p for p in unified_products 
        if (p.get('price', 0) == 0 or p.get('rating', 0) == 0 or p.get('reviews', 0) == 0) 
        and p.get('affiliate_url')
    ]
    
    if not products_needing_data:
        print("No products with missing data found!")
        return
    
    print(f"Found {len(products_needing_data)} products with missing data\n")
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("Chrome WebDriver initialized\n")
    except Exception as e:
        print(f"Failed to initialize Chrome: {e}")
        return
    
    updated_count = 0
    
    try:
        for idx, product in enumerate(products_needing_data, 1):
            asin = product['product_id']
            name = product['name'][:60]
            url = product['affiliate_url']
            
            needs_price = product.get('price', 0) == 0
            needs_rating = product.get('rating', 0) == 0
            needs_reviews = product.get('reviews', 0) == 0
            
            print(f"[{idx}/{len(products_needing_data)}] {asin}: {name}...")
            print(f"  Fetching data from: {url}")
            
            updated = False
            
            # Fetch price if needed
            if needs_price:
                price = extract_price_from_page(driver, url)
                if price > 0:
                    product['price'] = price
                    print(f"  [OK] Price: ${price:.2f}")
                    updated = True
                else:
                    print(f"  [FAILED] Could not extract price")
            
            # Fetch rating and reviews if needed
            if needs_rating or needs_reviews:
                rating, reviews = extract_rating_and_reviews_from_page(driver, url)
                if rating > 0:
                    product['rating'] = rating
                    print(f"  [OK] Rating: {rating:.1f} stars")
                    updated = True
                if reviews > 0:
                    product['reviews'] = reviews
                    print(f"  [OK] Reviews: {reviews:,}")
                    updated = True
            
            if updated:
                # Update in simple products
                simple_asin = asin
                with open(simple_file, 'r', encoding='utf-8') as f:
                    simple_products = json.load(f)
                
                for sp in simple_products:
                    if sp.get('asin') == simple_asin:
                        if needs_price and 'price' in product:
                            sp['price'] = product['price']
                        if needs_rating and 'rating' in product:
                            sp['rating'] = product['rating']
                        if needs_reviews and 'reviews' in product:
                            sp['reviews'] = product['reviews']
                        break
                
                with open(simple_file, 'w', encoding='utf-8') as f:
                    json.dump(simple_products, f, indent=2)
                
                updated_count += 1
            
            time.sleep(2)  # Rate limiting
        
        # Save updated unified products
        with open(unified_file, 'w', encoding='utf-8') as f:
            json.dump(unified_products, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"Data update complete!")
        print(f"  Updated: {updated_count}/{len(products_needing_data)}")
        print(f"{'='*60}")
        
    finally:
        driver.quit()
        print("\nChrome WebDriver closed")

if __name__ == '__main__':
    update_product_data()

