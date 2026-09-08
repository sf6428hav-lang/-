import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

print('=== Testing tikmate.app ===\n')

session = requests.Session()

# 尝试 API
api_url = 'https://api.tikmate.app/api/lookup'
r = session.post(api_url,
                data={'url': url},
                headers={'User-Agent': UA, 'Referer': 'https://tikmate.app/', 'Content-Type': 'application/json'},
                impersonate='chrome120',
                timeout=15)

print(f'Status: {r.status_code}')

if r.status_code == 200:
    try:
        data = r.json()
        print(f'Response: {json.dumps(data, indent=2, ensure_ascii=False)[:800]}')
        
        if 'data' in data:
            data_content = data['data']
            if isinstance(data_content, dict):
                print(f'\nData keys: {list(data_content.keys())}')
                if 'token' in data_content and 'id' in data_content:
                    print(f"✅ Download URL: /download/{data_content['token']}/{data_content['id']}.mp4")
    except Exception as e:
        print(f'Error: {str(e)[:100]}')
else:
    print(f'Response: {r.text[:300]}')

print('\n=== Testing more services ===\n')

services_to_test = [
    {'name': 'ssstik.io', 'homepage': 'https://ssstik.io/'},
    {'name': 'savetik.co', 'homepage': 'https://savetik.co/'},
    {'name': 'tikdown.app', 'homepage': 'https://tikdown.app/'},
]

for svc in services_to_test:
    print(f'=== {svc["name"]} ===')
    
    session2 = requests.Session()
    
    try:
        r_home = session2.get(svc['homepage'],
                             headers={'User-Agent': UA},
                             impersonate='chrome120',
                             timeout=10)
        
        print(f'Homepage: {r_home.status_code}')
        
        if r_home.status_code == 200:
            html = r_home.text
            
            # 查找API端点
            api_endpoints = re.findall(r'["\']([^"\']*(?:/api/|/ajax)[^"\']*)["\']', html)
            api_endpoints = list(set([ep for ep in api_endpoints if not ep.startswith('https://cdnjs') and not ep.startswith('https://pagead')]))[:10]
            
            if api_endpoints:
                print(f'API endpoints: {api_endpoints}')
            else:
                print('No API endpoints found')
    except Exception as e:
        print(f'Error: {str(e)[:80]}')
    
    print()
