import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

session = requests.Session()

# 测试 savetik.co 并解析 HTML
print('=== Testing savetik.co with HTML parsing ===\n')

r = session.post('https://savetik.co/api/ajaxSearch', 
                data={'q': url, 'lang': 'en'},
                headers={'User-Agent': UA, 'Referer': 'https://savetik.co/'},
                impersonate='chrome120',
                timeout=15)

if r.status_code == 200:
    data = r.json()
    if 'data' in data and isinstance(data['data'], str):
        html = data['data']
        print(f'HTML length: {len(html)} chars')
        
        # 查找视频下载链接
        links = re.findall(r'href=["\']([^"\']+)["\']', html)
        video_links = [l for l in links if 'video' in l.lower() or 'mp4' in l.lower() or 'download' in l.lower() or 'tiktok' in l.lower()]
        
        print(f'\nTotal links: {len(links)}')
        print(f'Video-related links: {len(video_links)}')
        if video_links:
            print('First 5 video links:')
            for link in video_links[:5]:
                print(f'  {link}')
        
        # 查找所有 URL
        all_urls = re.findall(r'https?://[^"\'<>\s]+', html)
        print(f'\nAll URLs: {len(all_urls)}')
        if all_urls:
            print('First 10 URLs:')
            for u in all_urls[:10]:
                print(f'  {u}')

print('\n' + '='*60 + '\n')

# 测试其他服务
print('=== Testing other services ===\n')

services_to_test = [
    {
        'name': 'dlpanda.com',
        'url': 'https://dlpanda.com/zh-CN',
        'js_files': ['https://dlpanda.com/build/assets/app-E5aetN4P.js']
    },
    {
        'name': 'snaptik.app',
        'url': 'https://snaptik.app/',
        'js_files': ['/js/core.min.js?v=1784883758', '/js/ui.min.js?v=1784883758']
    }
]

for svc in services_to_test:
    print(f'=== {svc["name"]} - Analyzing JS files ===')
    
    # 获取主页找 token
    r_main = session.get(svc['url'], headers={'User-Agent': UA}, impersonate='chrome120', timeout=15)
    html = r_main.text
    
    # 查找 CSRF token
    csrf_tokens = re.findall(r'name=["\']_token["\'][^>]+value=["\']([^"\']+)["\']', html)
    csrf_tokens += re.findall(r'name=["\']csrf[_-]?token["\'][^>]+value=["\']([^"\']+)["\']', html)
    
    if csrf_tokens:
        print(f'Found CSRF token: {csrf_tokens[0][:50]}...')
    else:
        print('No CSRF token found')
    
    # 查找第一个 JS 文件并分析
    if svc['js_files']:
        js_url = svc['js_files'][0]
        if not js_url.startswith('http'):
            js_url = svc['url'].rstrip('/') + js_url
        
        try:
            r_js = session.get(js_url, headers={'User-Agent': UA}, impersonate='chrome120', timeout=10)
            if r_js.status_code == 200:
                js_content = r_js.text
                print(f'JS file size: {len(js_content)} chars')
                
                # 查找 API 端点
                api_endpoints = re.findall(r'["\']([^"\']*(?:/api/|/ajax|/parse|/download|/extract)[^"\']*)["\']', js_content)
                print(f'API endpoints in JS: {api_endpoints[:10]}')
                
                # 查找 fetch/ajax 调用
                fetch_patterns = [
                    r'fetch\s*\(\s*["\']([^"\']+)["\']',
                    r'\.ajax\s*\(\s*\{[^}]*url:\s*["\']([^"\']+)["\']',
                    r'\.post\s*\(\s*["\']([^"\']+)["\']',
                    r'\.get\s*\(\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in fetch_patterns:
                    matches = re.findall(pattern, js_content)
                    if matches:
                        print(f'Pattern "{pattern[:20]}..." found: {matches[:5]}')
        except Exception as e:
            print(f'Failed to fetch JS: {e}')
    
    print()
