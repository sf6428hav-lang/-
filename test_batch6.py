import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

services = [
    {'name': 'ttget.net', 'url': 'https://ttget.net/'},
    {'name': 'xiazaitool.com', 'url': 'https://www.xiazaitool.com/douyin'},
    {'name': 'kukutool.com', 'url': 'https://www.kukutool.com/zh-cn/douyin-video-download'},
    {'name': 'musicallydown.com', 'url': 'https://musicallydown.com/'},
    {'name': 'qload.info', 'url': 'https://qload.info/'},
    {'name': 'tikmate.app', 'url': 'https://tikmate.app/'},
]

print('=== Testing 6 additional services ===\n')

for svc in services:
    print(f'=== {svc["name"]} ===')
    try:
        session = requests.Session()
        r = session.get(svc['url'], 
                       headers={'User-Agent': UA},
                       impersonate='chrome120',
                       timeout=15)
        print(f'Status: {r.status_code}')
        
        if r.status_code == 200:
            html = r.text
            print(f'HTML length: {len(html)} chars')
            
            # Find forms
            forms = re.findall(r'<form[^>]*action=["\']([^"\']+)["\'][^>]*>', html)
            print(f'Forms: {forms[:5]}')
            
            # Find API endpoints
            api_endpoints = re.findall(r'["\']([^"\']*(?:/api/|/ajax|/parse|/download|/extract|/convert)[^"\']*)["\']', html)
            print(f'API endpoints: {api_endpoints[:10]}')
            
            # Find fetch calls
            fetch_calls = re.findall(r'fetch\s*\(\s*["\']([^"\']+)["\']', html)
            print(f'Fetch calls: {fetch_calls[:5]}')
            
            # Find CSRF tokens
            csrf = re.findall(r'name=["\']_token["\'][^>]+value=["\']([^"\']+)["\']', html)
            csrf += re.findall(r'name=["\']csrf[_-]?token["\'][^>]+value=["\']([^"\']+)["\']', html)
            csrf += re.findall(r'name=["\']token["\'][^>]+value=["\']([^"\']+)["\']', html)
            if csrf:
                print(f'CSRF token found: {csrf[0][:50]}...')
            
            # Find JS files
            js_files = re.findall(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', html)
            print(f'JS files: {js_files[:5]}')
            
        else:
            print(f'Failed: {r.text[:200]}')
    except Exception as e:
        print(f'Error: {str(e)[:150]}')
    
    print()
