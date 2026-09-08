import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

print('=== Deep testing snaptik.life ===\n')

session = requests.Session()

# 测试下载页面
download_pages = [
    'https://snaptik.life/download-tiktok-mp4/',
    'https://snaptik.life/download-tiktok-photo/',
    'https://snaptik.life/download-story-tiktok/'
]

for page_url in download_pages:
    print(f'Testing: {page_url}')
    
    r = session.get(page_url,
                   headers={'User-Agent': UA, 'Referer': 'https://snaptik.life/'},
                   impersonate='chrome120',
                   timeout=10)
    
    print(f'Status: {r.status_code}')
    
    if r.status_code == 200:
        html = r.text
        
        # 查找API端点
        api_endpoints = re.findall(r'["\']([^"\']*(?:/api/|/ajax|/parse|/download)[^"\']*)["\']', html)
        api_endpoints = list(set([ep for ep in api_endpoints if not ep.startswith('https://cdnjs') and not ep.startswith('https://pagead') and not ep.startswith('https://cdn.') and not ep.startswith('/img/')]))[:15]
        
        if api_endpoints:
            print(f'API endpoints: {api_endpoints}')
            
            # 查找CSRF token
            csrf = re.findall(r'name=["\']_token["\'][^>]+value=["\']([^"\']+)["\']', html)
            csrf += re.findall(r'name=["\']csrf[_-]?token["\'][^>]+value=["\']([^"\']+)["\']', html)
            csrf += re.findall(r'name=["\']token["\'][^>]+value=["\']([^"\']+)["\']', html)
            
            # 尝试常见的API路径
            for api_path in ['/api/ajaxSearch', '/api/parse', '/api/download', '/parse', '/download']:
                try:
                    api_url = page_url.rstrip('/') + api_path
                    r2 = session.post(api_url,
                                   data={'q': url, 'url': url, 'lang': 'en', '_token': csrf[0] if csrf else ''},
                                   headers={'User-Agent': UA, 'Referer': page_url},
                                   impersonate='chrome120',
                                   timeout=10)
                    
                    if r2.status_code == 200:
                        print(f'✅ {api_path} works!')
                        try:
                            data = r2.json()
                            print(f'  Response keys: {list(data.keys())[:8]}')
                            if 'data' in data or 'video_url' in data or 'url' in data or 'video' in data:
                                print(f'  ✅ Has video data!')
                                data_str = json.dumps(data)
                                video_urls = re.findall(r'https?://[^"\'<>\s]+', data_str)
                                video_cdn = [u for u in video_urls if 'zjcdn' in u or 'douyinvod' in u or 'bytedance' in u or 'douyin' in u.lower()]
                                if video_cdn:
                                    print(f'  ✅ Found {len(video_cdn)} video CDN links')
                                    print(f'  First: {video_cdn[0][:100]}...')
                                    break
                        except:
                            if 'video' in r2.text.lower() or 'mp4' in r2.text.lower():
                                print(f'  ✅ HTML contains video references')
                                video_urls = re.findall(r'https?://[^"\'<>\s]+', r2.text)
                                video_cdn = [u for u in video_urls if 'zjcdn' in u or 'douyinvod' in u or 'bytedance' in u or 'douyin' in u.lower()]
                                if video_cdn:
                                    print(f'  ✅ Found {len(video_cdn)} video CDN links')
                                    print(f'  First: {video_cdn[0][:100]}...')
                                    break
                except:
                    pass
        else:
            print('No API endpoints found')
    
    print()

print('\n=== Testing nowatermarkdl.com deeper ===\n')

session2 = requests.Session()

r_home = session2.get('https://nowatermarkdl.com/',
                     headers={'User-Agent': UA},
                     impersonate='chrome120',
                     timeout=10)

print(f'Homepage: {r_home.status_code}')

if r_home.status_code == 200:
    html = r_home.text
    
    # 查找表单
    forms = re.findall(r'<form[^>]*>(.*?)</form>', html, re.DOTALL)
    print(f'Forms found: {len(forms)}')
    
    # 查找所有链接
    links = re.findall(r'href=["\']([^"\']+)["\']', html)
    print(f'Links found: {len(links)}')
    
    # 过滤出可能的API路径
    api_links = [l for l in links if '/api/' in l or '/ajax' in l or '/parse' in l or '/download' in l]
    print(f'API-like links: {api_links[:10]}')
    
    # 尝试常见的API路径
    for api_path in ['/api/ajaxSearch', '/api/parse', '/api/download', '/parse', '/download']:
        try:
            api_url = 'https://nowatermarkdl.com' + api_path
            r = session2.post(api_url,
                           data={'q': url, 'url': url, 'lang': 'en'},
                           headers={'User-Agent': UA, 'Referer': 'https://nowatermarkdl.com/'},
                           impersonate='chrome120',
                           timeout=10)
            
            if r.status_code == 200:
                print(f'✅ {api_path} works!')
                try:
                    data = r.json()
                    print(f'  Response keys: {list(data.keys())[:8]}')
                except:
                    pass
                break
        except:
            pass

print('\n=== Testing tiktokdownloader.com deeper ===\n')

session3 = requests.Session()

r_home = session3.get('https://tiktokdownloader.com/',
                     headers={'User-Agent': UA},
                     impersonate='chrome120',
                     timeout=10)

print(f'Homepage: {r_home.status_code}')

if r_home.status_code == 200:
    html = r_home.text
    
    # 查找表单
    forms = re.findall(r'<form[^>]*>(.*?)</form>', html, re.DOTALL)
    print(f'Forms found: {len(forms)}')
    
    # 查找所有链接
    links = re.findall(r'href=["\']([^"\']+)["\']', html)
    print(f'Links found: {len(links)}')
    
    # 过滤出可能的API路径
    api_links = [l for l in links if '/api/' in l or '/ajax' in l or '/parse' in l or '/download' in l]
    print(f'API-like links: {api_links[:10]}')
    
    # 尝试常见的API路径
    for api_path in ['/api/ajaxSearch', '/api/parse', '/api/download', '/parse', '/download']:
        try:
            api_url = 'https://tiktokdownloader.com' + api_path
            r = session3.post(api_url,
                           data={'q': url, 'url': url, 'lang': 'en'},
                           headers={'User-Agent': UA, 'Referer': 'https://tiktokdownloader.com/'},
                           impersonate='chrome120',
                           timeout=10)
            
            if r.status_code == 200:
                print(f'✅ {api_path} works!')
                try:
                    data = r.json()
                    print(f'  Response keys: {list(data.keys())[:8]}')
                except:
                    pass
                break
        except:
            pass
