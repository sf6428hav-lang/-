import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

services = [
    {'name': 'ssstik.io', 'url': 'https://ssstik.io/', 'method': 'POST', 'data': {'id': url, 'locale': 'en', 'tt': 'ttvalue'}},
    {'name': 'snaptik.app', 'url': 'https://snaptik.app/', 'method': 'POST', 'data': {'url': url}},
    {'name': 'tikdownloader.app', 'url': 'https://tikdownloader.app/api/ajaxSearch', 'method': 'POST', 'data': {'q': url, 'lang': 'en'}},
]

print('=== Testing more services with curl_cffi ===\n')

for svc in services:
    print(f'=== {svc["name"]} ===')
    
    session = requests.Session()
    
    # 先获取主页
    r_home = session.get(svc['url'].split('/api')[0], 
                         headers={'User-Agent': UA},
                         impersonate='chrome120',
                         timeout=15)
    
    if r_home.status_code == 200:
        html = r_home.text
        
        # 查找 CSRF token
        csrf = re.findall(r'name=["\']_token["\'][^>]+value=["\']([^"\']+)["\']', html)
        csrf += re.findall(r'name=["\']csrf[_-]?token["\'][^>]+value=["\']([^"\']+)["\']', html)
        csrf += re.findall(r'name=["\']token["\'][^>]+value=["\']([^"\']+)["\']', html)
        
        if csrf:
            print(f'Found token: {csrf[0][:50]}...')
            # 添加 token 到请求数据
            svc['data']['_token'] = csrf[0]
        
        # 发送请求
        if svc['method'] == 'POST':
            r = session.post(svc['url'], 
                           data=svc['data'],
                           headers={'User-Agent': UA, 'Referer': svc['url'].split('/api')[0]},
                           impersonate='chrome120',
                           timeout=15)
        
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            try:
                data = r.json()
                print(f'JSON keys: {list(data.keys())[:10]}')
                if 'data' in data:
                    print(f'Has data field')
                if 'video' in str(data).lower() or 'mp4' in str(data).lower():
                    print('✅ Contains video data!')
                    print(f'Response: {json.dumps(data, indent=2, ensure_ascii=False)[:800]}')
            except:
                print('Not JSON')
                if 'video' in r.text.lower() or 'mp4' in r.text.lower():
                    print('✅ HTML contains video references')
                    links = re.findall(r'https?://[^"\'<>\s]+', r.text)
                    video_links = [l for l in links if 'video' in l.lower() or 'mp4' in l.lower()]
                    print(f'Video links: {video_links[:3]}')
        else:
            print(f'Failed: {r.text[:200]}')
    else:
        print(f'Homepage failed: {r_home.status_code}')
    
    print()
