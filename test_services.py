import httpx
import json

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

print('=== Testing botvod /api/info ===')
try:
    r = httpx.post('https://www.botvod.com/api/info', 
                   json={'url': url},
                   headers={'User-Agent': UA, 'Referer': 'https://www.botvod.com/'},
                   timeout=30)
    print(f'Status: {r.status_code}')
    data = r.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f'Error: {e}')
