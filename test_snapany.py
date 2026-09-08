import httpx
import json
import re

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
url = 'https://v.douyin.com/1CzGfFJVQD0/'

# Test snapany
print('=== snapany.com ===')
try:
    # First get the page to find API endpoints
    r = httpx.get('https://snapany.com/zh', headers={'User-Agent': UA}, timeout=15)
    html = r.text
    
    # Look for API calls in the page
    api_patterns = re.findall(r'[\"\x27](/api/[^\"\x27]+)[\"\x27]', html)
    print(f'API endpoints found: {api_patterns[:10]}')
    
    # Try common Next.js API patterns
    for endpoint in ['/api/parse', '/api/download', '/api/v1/parse', '/api/extract']:
        try:
            r2 = httpx.post(f'https://snapany.com{endpoint}', 
                           json={'url': url},
                           headers={'User-Agent': UA, 'Referer': 'https://snapany.com/zh'},
                           timeout=15)
            print(f'{endpoint}: {r2.status_code} - {r2.text[:200]}')
            if r2.status_code == 200:
                break
        except:
            pass
except Exception as e:
    print(f'Error: {e}')

print()

# Test more services
more_services = [
    {'name': 'douyin.wtf', 'url': 'https://api.douyin.wtf/api?url=' + url, 'method': 'GET'},
    {'name': 'tiktok-saver', 'url': 'https://tiktok-saver.com/api', 'method': 'POST', 'data': {'url': url}},
    {'name': 'tikmate.online', 'url': 'https://tikmate.online/api/ajaxSearch', 'method': 'POST', 'data': {'q': url, 'lang': 'en'}},
    {'name': 'tikdownloader', 'url': 'https://tikdownloader.io/api/ajaxSearch', 'method': 'POST', 'data': {'q': url, 'lang': 'en'}},
]

for svc in more_services:
    print(f"=== {svc['name']} ===")
    try:
        headers = {'User-Agent': UA}
        if svc['method'] == 'POST':
            r = httpx.post(svc['url'], data=svc['data'], headers=headers, timeout=15)
        else:
            r = httpx.get(svc['url'], headers=headers, timeout=15)
        print(f'Status: {r.status_code}')
        print(r.text[:500])
    except Exception as e:
        print(f'Error: {e}')
    print()
