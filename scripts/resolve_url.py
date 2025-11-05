import requests
import re

url = 'https://amzn.to/3LtpYfE'
try:
    r = requests.head(url, allow_redirects=True, timeout=10)
    print(f'Resolved URL: {r.url}')
    asin = re.search(r'/dp/([A-Z0-9]{10})', r.url)
    print(f'ASIN: {asin.group(1) if asin else "NOT_FOUND"}')
except Exception as e:
    print(f'Error: {e}')
