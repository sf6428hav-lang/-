import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

services_to_test = [
    {'name': 'tiktokdownload.online', 'homepage': 'https://tiktokdownload.online/'},
    {'name': 'nowatermarkdl.com', 'homepage': 'https://nowatermarkdl.com/'},
    {'name': 'tiktokdownloader.com', 'homepage': 'https://tiktokdownloader.com/'},
    {'name': 'easydown.vip', 'homepage': 'https://easydown.vip/'},
    {'name': 'yinziai.com', 'homepage': 'https://yinziai.com/'},
    {'name': 'snaptik.life', 'homepage': 'https://snaptik.life/'},
]

print('=== Testing new batch of services ===\n')

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
            api_endpoints = list(set([ep for ep in api_endpoints if not ep.startswith('https://cdnjs') and not ep.startswith('https://pagead') and not ep.startswith('https://cdn.')]))[:10]
            
            if api_endpoints:
                print(f'API endpoints: {api_endpoints}')
                
                # 查找CSRF token
                csrf = re.findall(r'name=["\']_token["\'][^>]+value=["\']([^"\']+)["\']', html)
                csrf += re.findall(r'name=["\']csrf[_-]?token["\'][^>]+value=["\']([^"\']+)["\']', html)
                csrf += re.findall(r'name=["\']token["\'][^>]+value=["\']([^"\']+)["\']', html)
                
                # 尝试常见的API路径
                for api_path in ['/api/ajaxSearch', '/api/parse', '/api/download', '/api/v1/parse', '/parse', '/download', '/api/extract']:
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
                                print(f'  Response keys: {list(data.keys())[:8]}')
                                if 'data' in data or 'video_url' in data or 'url' in data or 'video' in data:
                                    print(f'  ✅ Has video data!')
                                    
                                    # 尝试提取视频链接
                                    data_str = json.dumps(data)
                                    video_urls = re.findall(r'https?://[^"\'<>\s]+', data_str)
                                    video_cdn = [u for u in video_urls if 'zjcdn' in u or 'douyinvod' in u or 'bytedance' in u or 'douyin' in u.lower()]
                                    if video_cdn:
                                        print(f'  ✅ Found {len(video_cdn)} video CDN links')
                                        print(f'  First: {video_cdn[0][:100]}...')
                                        break
                            except:
                                if 'video' in r.text.lower() or 'mp4' in r.text.lower():
                                    print(f'  ✅ HTML contains video references')
                                    video_urls = re.findall(r'https?://[^"\'<>\s]+', r.text)
                                    video_cdn = [u for u in video_urls if 'zjcdn' in u or 'douyinvod' in u or 'bytedance' in u or 'douyin' in u.lower()]
                                    if video_cdn:
                                        print(f'  ✅ Found {len(video_cdn)} video CDN links')
                                        print(f'  First: {video_cdn[0][:100]}...')
                                        break
                    except:
                        pass
            else:
                print('No API endpoints found in HTML')
        else:
            print(f'Homepage failed: {r_home.status_code}')
    except Exception as e:
        print(f'Error: {str(e)[:80]}')
    
    print()
