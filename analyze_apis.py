import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

services = [
    {'name': 'dlpanda.com', 'url': 'https://dlpanda.com/zh-CN'},
    {'name': 'snaptik.app', 'url': 'https://snaptik.app/'},
    {'name': 'ssstik.io', 'url': 'https://ssstik.io/'},
    {'name': 'savetik.co', 'url': 'https://savetik.co/'},
]

print('=== 深入分析 API 调用 ===')

for svc in services:
    print(f'\n=== {svc["name"]} ===')
    try:
        session = requests.Session()
        r = session.get(svc['url'], headers={'User-Agent': UA}, impersonate='chrome120', timeout=15)
        
        if r.status_code == 200:
            html = r.text
            
            # 查找 JS 文件
            js_files = re.findall(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', html)
            print(f'JS files: {js_files[:5]}')
            
            # 查找内联 JS 中的 API 调用
            inline_js = re.findall(r'<script[^>]*>(.+?)</script>', html, re.DOTALL)
            
            for js_block in inline_js:
                if 'fetch' in js_block or 'ajax' in js_block or '/api/' in js_block:
                    print(f'Found inline JS with API calls')
                    
                    # 提取 API 端点
                    api_endpoints = re.findall(r'["\']([^"\']*(?:/api/|/ajax|/parse|/download)[^"\']*)["\']', js_block)
                    print(f'  API endpoints: {api_endpoints[:10]}')
                    
                    # 提取 fetch/ajax 调用
                    fetch_calls = re.findall(r'(?:fetch|\.ajax|\.post|\.get)\s*\(\s*["\']([^"\']+)["\']', js_block)
                    print(f'  Fetch calls: {fetch_calls[:10]}')
                    
                    # 尝试找到的 API
                    for endpoint in api_endpoints[:3]:
                        if not endpoint.startswith('http'):
                            endpoint = svc['url'].rstrip('/') + endpoint
                        try:
                            r2 = session.post(endpoint, data={'url': url, 'lang': 'en'}, headers={'User-Agent': UA, 'Referer': svc['url']}, impersonate='chrome120', timeout=15)
                            if r2.status_code == 200:
                                try:
                                    data = r2.json()
                                    print(f'  {endpoint} => JSON keys: {list(data.keys())[:5]}')
                                except:
                                    print(f'  {endpoint} => HTML {len(r2.text)} bytes')
                        except:
                            pass
            
            # 尝试常见 API 路径
            common_paths = ['/api/ajaxSearch', '/api/parse', '/api/download', '/api/v1/parse', '/api/extract']
            for path in common_paths:
                try:
                    api_url = svc['url'].rstrip('/') + path
                    r2 = session.post(api_url, data={'url': url, 'lang': 'en', 'q': url}, headers={'User-Agent': UA, 'Referer': svc['url']}, impersonate='chrome120', timeout=10)
                    if r2.status_code == 200:
                        try:
                            data = r2.json()
                            print(f'{path} => JSON keys: {list(data.keys())[:8]}')
                            # 检查是否有视频 URL
                            text = str(data)
                            if 'video' in text.lower() or 'url' in text.lower() or 'link' in text.lower():
                                print(f'  可能包含视频信息!')
                        except:
                            pass
                except:
                    pass
    
    except Exception as e:
        print(f'Error: {str(e)[:150]}')
