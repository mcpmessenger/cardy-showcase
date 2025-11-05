import requests
import re

urls = ['https://amzn.to/47XQoin', 'https://amzn.to/49Cf15v']

for url in urls:
    try:
        r = requests.head(url, allow_redirects=True, timeout=10)
        asin = re.search(r'/dp/([A-Z0-9]{10})', r.url)
        print(f'{url} -> {r.url}')
        print(f'ASIN: {asin.group(1) if asin else "NOT_FOUND"}')
    except Exception as e:
        print(f'Error resolving {url}: {e}')

