import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

services_to_test = [
    {'name': 'tikviral.com', 'url': 'https://tikviral.com/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
    {'name': 'tikwm.app', 'url': 'https://www.tikwm.com/api/', 'data': {'url': url, 'hd': 1}},
    {'name': 'tikcdn.io', 'url': 'https://tikcdn.io/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
    {'name': 'tikmate.online', 'url': 'https://tikmate.online/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
    {'name': 'tiklydown.com', 'url': 'https://tiklydown.com/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
]

print('=== Testing more services with curl_cffi ===\n')

for svc in services_to_test:
    print(f'=== {svc["name"]} ===')
    
    session = requests.Session()
    
    # 先获取主页
    homepage = svc['url'].split('/api')[0]
    try:
        r_home = session.get(homepage, 
                             headers={'User-Agent': UA},
                             impersonate='chrome120',
                             timeout=15)
        
        if r_home.status_code == 200:
            print(f'Homepage: OK')
            
            # 查找 CSRF token
            html = r_home.text
            csrf = re.findall(r'name=["\']_token["\'][^>]+value=["\']([^"\']+)["\']', html)
            csrf += re.findall(r'name=["\']csrf[_-]?token["\'][^>]+value=["\']([^"\']+)["\']', html)
            
            if csrf:
                print(f'Found CSRF token')
                svc['data']['_token'] = csrf[0]
            
            # 发送 API 请求
            r = session.post(svc['url'], 
                           data=svc['data'],
                           headers={'User-Agent': UA, 'Referer': homepage},
                           impersonate='chrome120',
                           timeout=15)
            
            print(f'API Status: {r.status_code}')
            
            if r.status_code == 200:
                try:
                    data = r.json()
                    print(f'JSON keys: {list(data.keys())[:10]}')
                    
                    # 检查是否有视频数据
                    if 'data' in data:
                        data_content = data['data']
                        if isinstance(data_content, str):
                            # 搜索视频链接
                            video_urls = re.findall(r'https?://[^"\'<>\s]+', data_content)
                            video_cdn = [u for u in video_urls if 'douyinvod' in u or 'douyinpic' in u or 'zjcdn' in u or 'bytedance' in u or 'video' in u.lower()]
                            
                            if video_cdn:
                                print(f'✅ Found {len(video_cdn)} video CDN links')
                                print(f'First link: {video_cdn[0][:100]}...')
                        elif isinstance(data_content, dict):
                            if 'video_url' in data_content or 'url' in data_content:
                                print(f'✅ Has video URL field')
                                print(f'Video URL: {data_content.get("video_url") or data_content.get("url")}')
                    
                    if 'video_url' in data:
                        print(f'✅ Direct video_url: {data["video_url"][:100]}...')
                        
                except:
                    print('Not JSON')
            else:
                print(f'Failed: {r.text[:150]}')
        else:
            print(f'Homepage failed: {r_home.status_code}')
    except Exception as e:
        print(f'Error: {str(e)[:100]}')
    
    print()
