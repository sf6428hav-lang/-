import httpx
import json
import re

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
url = 'https://v.douyin.com/1CzGfFJVQD0/'

# Test various known free services
services = [
    {'name': 'ssstik.io', 'url': 'https://ssstik.io/abc', 'method': 'POST', 'data': {'id': url, 'locale': 'en', 'tt': 'try'}},
    {'name': 'snaptik.app', 'url': 'https://snaptik.app/abc2', 'method': 'POST', 'data': {'url': url, 'lang': 'en'}},
    {'name': 'tikwm.com', 'url': 'https://www.tikwm.com/api/', 'method': 'POST', 'data': {'url': url, 'hd': 1}},
    {'name': 'tikcdn.io', 'url': 'https://tikcdn.io/api/parse', 'method': 'POST', 'data': {'url': url}},
]

for svc in services:
    print(f"=== {svc['name']} ===")
    try:
        headers = {'User-Agent': UA, 'Referer': svc['url'].rsplit('/', 1)[0] + '/'}
        if svc['method'] == 'POST':
            r = httpx.post(svc['url'], data=svc['data'], headers=headers, timeout=15)
        else:
            r = httpx.get(svc['url'], params=svc['data'], headers=headers, timeout=15)
        print(f'Status: {r.status_code}')
        text = r.text[:1000]
        print(text)
    except Exception as e:
        print(f'Error: {e}')
    print()
