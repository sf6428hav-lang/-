import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

print('=== Testing common API patterns ===\n')

services_to_test = [
    {'name': 'snaptik.life', 'base': 'https://snaptik.life'},
    {'name': 'tiktokdownload.online', 'base': 'https://tiktokdownload.online'},
    {'name': 'tiktokdownloader.com', 'base': 'https://tiktokdownloader.com'},
    {'name': 'nowatermarkdl.com', 'base': 'https://nowatermarkdl.com'},
]

common_endpoints = [
    '/api/ajaxSearch',
    '/api/download',
    '/api/extract',
    '/api/parse',
    '/api/video',
    '/api/process',
    '/download',
    '/extract',
]

for svc in services_to_test:
    print(f'\n=== {svc["name"]} ===')
    session = requests.Session()
    
    for endpoint in common_endpoints:
        try:
            api_url = svc['base'] + endpoint
            r = session.post(api_url,
                           data={'url': url, 'q': url, 'link': url},
                           headers={'User-Agent': UA, 'Referer': svc['base'] + '/'},
                           impersonate='chrome120',
                           timeout=8)
            
            if r.status_code == 200:
                print(f'✅ {endpoint} - Status 200')
                try:
                    data = r.json()
                    print(f'   JSON keys: {list(data.keys())[:8]}')
                    
                    # 检查是否有视频链接
                    data_str = json.dumps(data)
                    if 'video' in data_str.lower() or 'mp4' in data_str.lower() or 'url' in data_str.lower():
                        video_urls = re.findall(r'https?://[^"\'<>\s]+', data_str)
                        video_cdn = [u for u in video_urls if 'douyinvod' in u or 'bytedance' in u or 'zjcdn' in u or 'douyin' in u.lower()]
                        if video_cdn:
                            print(f'   ✅ Found {len(video_cdn)} video URLs!')
                            print(f'   First: {video_cdn[0][:100]}...')
                            break
                except:
                    if 'video' in r.text.lower() or 'mp4' in r.text.lower():
                        print(f'   HTML contains video references')
                        break
            elif r.status_code != 404:
                print(f'   {endpoint} - Status {r.status_code}')
        except Exception as e:
            pass

print('\n\n=== Testing with form submission ===\n')

for svc in services_to_test:
    print(f'\n=== {svc["name"]} - Form submission ===')
    session = requests.Session()
    
    # 获取主页找 CSRF token
    r_home = session.get(svc['base'] + '/',
                        headers={'User-Agent': UA},
                        impersonate='chrome120',
                        timeout=10)
    
    if r_home.status_code == 200:
        html = r_home.text
        
        # 查找 CSRF token
        csrf_patterns = [
            r'name=["\']csrf[_-]?token["\'][^>]*value=["\']([^"\']+)["\']',
            r'name=["\']_token["\'][^>]*value=["\']([^"\']+)["\']',
            r'name=["\']token["\'][^>]*value=["\']([^"\']+)["\']',
            r'csrf[_-]?token["\']\s*:\s*["\']([^"\']+)["\']',
            r'_token["\']\s*:\s*["\']([^"\']+)["\']',
        ]
        
        csrf_token = None
        for pattern in csrf_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                csrf_token = match.group(1)
                print(f'Found CSRF token: {csrf_token[:50]}...')
                break
        
        # 查找表单 action
        form_match = re.search(r'<form[^>]*action=["\']([^"\']+)["\']', html)
        if form_match:
            form_action = form_match.group(1)
            print(f'Found form action: {form_action}')
            
            # 提交表单
            form_url = svc['base'] + form_action if not form_action.startswith('http') else form_action
            form_data = {'url': url, 'link': url, 'q': url}
            if csrf_token:
                form_data['_token'] = csrf_token
                form_data['csrf_token'] = csrf_token
            
            r_form = session.post(form_url,
                                data=form_data,
                                headers={'User-Agent': UA, 'Referer': svc['base'] + '/'},
                                impersonate='chrome120',
                                timeout=10)
            
            print(f'Form submission status: {r_form.status_code}')
            
            if r_form.status_code == 200:
                try:
                    data = r_form.json()
                    print(f'JSON keys: {list(data.keys())[:8]}')
                except:
                    if 'video' in r_form.text.lower() or 'mp4' in r_form.text.lower():
                        print('HTML contains video references')
                        video_urls = re.findall(r'https?://[^"\'<>\s]+', r_form.text)
                        video_cdn = [u for u in video_urls if 'douyinvod' in u or 'bytedance' in u or 'zjcdn' in u]
                        if video_cdn:
                            print(f'✅ Found {len(video_cdn)} video URLs!')
                            print(f'First: {video_cdn[0][:100]}...')
