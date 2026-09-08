import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

services_to_test = [
    {'name': 'snaptik.app', 'url': 'https://snaptik.app/abc2', 'data': {'url': url}},
    {'name': 'tikwm.com', 'url': 'https://www.tikwm.com/api/', 'data': {'url': url, 'hd': 1}},
]

print('=== Testing remaining services ===\n')

for svc in services_to_test:
    print(f'=== {svc["name"]} ===')
    
    session = requests.Session()
    
    try:
        r = session.post(svc['url'], 
                       data=svc['data'],
                       headers={'User-Agent': UA},
                       impersonate='chrome120',
                       timeout=15)
        
        print(f'Status: {r.status_code}')
        
        if r.status_code == 200:
            try:
                data = r.json()
                print(f'JSON keys: {list(data.keys())[:10]}')
                
                if 'data' in data:
                    data_content = data['data']
                    if isinstance(data_content, str):
                        video_urls = re.findall(r'https?://[^"\'<>\s]+', data_content)
                        video_cdn = [u for u in video_urls if 'douyinvod' in u or 'douyinpic' in u or 'zjcdn' in u or 'bytedance' in u or 'video' in u.lower()]
                        
                        if video_cdn:
                            print(f'✅ Found {len(video_cdn)} video CDN links')
                            print(f'First: {video_cdn[0][:100]}...')
                    elif isinstance(data_content, dict):
                        if 'url' in data_content or 'video_url' in data_content:
                            print(f'✅ Has video URL')
                            print(f'URL: {data_content.get("url") or data_content.get("video_url")}')
                
                if 'url' in data:
                    print(f'✅ Direct url: {data["url"][:100]}...')
                    
            except:
                print('Not JSON')
        else:
            print(f'Failed: {r.text[:150]}')
    except Exception as e:
        print(f'Error: {str(e)[:100]}')
    
    print()
