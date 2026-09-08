import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# 测试更多可能的服务
services_to_test = [
    {'name': 'tiktoksaver.com', 'homepage': 'https://tiktoksaver.com/'},
    {'name': 'tikdownloader.io', 'homepage': 'https://tikdownloader.io/'},
    {'name': 'tiktokvideodownloader.com', 'homepage': 'https://tiktokvideodownloader.com/'},
    {'name': 'tiktokdownloader.app', 'homepage': 'https://tiktokdownloader.app/'},
    {'name': 'snaptik.to', 'homepage': 'https://snaptik.to/'},
]

print('=== Testing additional services ===\n')

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
            api_endpoints = re.findall(r'["\']([^"\']*(?:/api/|/ajax|/parse|/download)[^"\']*)["\']', html)
            api_endpoints = list(set(api_endpoints))[:10]
            
            print(f'API endpoints found: {api_endpoints}')
            
            # 查找表单action
            forms = re.findall(r'<form[^>]*action=["\']([^"\']+)["\']', html)
            print(f'Forms found: {forms}')
            
            # 查找CSRF token
            csrf = re.findall(r'name=["\']_token["\'][^>]+value=["\']([^"\']+)["\']', html)
            csrf += re.findall(r'name=["\']csrf[_-]?token["\'][^>]+value=["\']([^"\']+)["\']', html)
            
            if csrf:
                print(f'CSRF token found')
                
                # 尝试常见的API路径
                for api_path in ['/api/ajaxSearch', '/api/parse', '/api/download', '/parse', '/download']:
                    try:
                        api_url = svc['homepage'].rstrip('/') + api_path
                        r = session.post(api_url,
                                       data={'q': url, 'url': url, '_token': csrf[0]},
                                       headers={'User-Agent': UA, 'Referer': svc['homepage']},
                                       impersonate='chrome120',
                                       timeout=10)
                        
                        if r.status_code == 200:
                            print(f'✅ {api_path} works!')
                            try:
                                data = r.json()
                                print(f'  Response keys: {list(data.keys())[:8]}')
                                if 'data' in data or 'video_url' in data or 'url' in data:
                                    print(f'  ✅ Has video data!')
                                    break
                            except:
                                if 'video' in r.text.lower() or 'mp4' in r.text.lower():
                                    print(f'  ✅ HTML contains video references')
                                    break
                    except:
                        pass
        else:
            print(f'Homepage failed')
    except Exception as e:
        print(f'Error: {str(e)[:80]}')
    
    print()
