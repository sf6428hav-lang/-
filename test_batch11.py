import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

services_to_test = [
    {'name': 'tikdown.org', 'homepage': 'https://tikdown.org/'},
    {'name': 'tiktoksaver.online', 'homepage': 'https://tiktoksaver.online/'},
    {'name': 'tikly.io', 'homepage': 'https://tikly.io/'},
    {'name': 'tiksave.io', 'homepage': 'https://tiksave.io/'},
    {'name': 'tikmate.online', 'homepage': 'https://tikmate.online/'},
    {'name': 'snaptik.pro', 'homepage': 'https://snaptik.pro/'},
    {'name': 'tikdownload.net', 'homepage': 'https://tikdownload.net/'},
    {'name': 'tiktokdownloader.online', 'homepage': 'https://tiktokdownloader.online/'},
    {'name': 'snaptikapp.cc', 'homepage': 'https://snaptikapp.cc/'},
]

print('=== Testing more services ===\n')

for svc in services_to_test:
    print(f'=== {svc["name"]} ===')
    
    session = requests.Session()
    
    try:
        r_home = session.get(svc['homepage'],
                             headers={'User-Agent': UA},
                             impersonate='chrome120',
                             timeout=10)
        
        print(f'Homepage: {r_home.status_code}')
        
        if r_home.status_code == 200:
            html = r_home.text
            
            # 查找API端点
            api_endpoints = re.findall(r'["\']([^"\']*(?:/api/|/ajax)[^"\']*)["\']', html)
            api_endpoints = list(set(api_endpoints))[:5]
            
            if api_endpoints:
                print(f'API endpoints: {api_endpoints}')
                
                # 查找CSRF token
                csrf = re.findall(r'name=["\']_token["\'][^>]+value=["\']([^"\']+)["\']', html)
                csrf += re.findall(r'name=["\']csrf[_-]?token["\'][^>]+value=["\']([^"\']+)["\']', html)
                
                # 尝试常见的API路径
                for api_path in ['/api/ajaxSearch', '/api/parse', '/api/download']:
                    try:
                        api_url = svc['homepage'].rstrip('/') + api_path
                        r = session.post(api_url,
                                       data={'q': url, 'url': url, 'lang': 'en', '_token': csrf[0] if csrf else ''},
                                       headers={'User-Agent': UA, 'Referer': svc['homepage']},
                                       impersonate='chrome120',
                                       timeout=10)
                        
                        if r.status_code == 200:
                            print(f'✅ {api_path} works!')
                            try:
                                data = r.json()
                                if 'data' in data or 'video_url' in data or 'url' in data:
                                    print(f'  ✅ Has video data!')
                                    break
                            except:
                                if 'video' in r.text.lower() or 'mp4' in r.text.lower():
                                    print(f'  ✅ HTML contains video references')
                                    break
                    except:
                        pass
    except Exception as e:
        print(f'Error: {str(e)[:80]}')
    
    print()
