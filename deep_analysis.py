import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

session = requests.Session()

print('=== Deep analysis of ssstik.io ===\n')

r = session.get('https://ssstik.io/', 
                headers={'User-Agent': UA},
                impersonate='chrome120',
                timeout=15)

if r.status_code == 200:
    html = r.text
    
    # Look for JavaScript files
    js_files = re.findall(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', html)
    print(f'JavaScript files: {js_files[:10]}')
    
    # Look for inline scripts
    inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    print(f'\nInline scripts found: {len(inline_scripts)}')
    
    for i, script in enumerate(inline_scripts):
        if 'fetch' in script or 'ajax' in script or '/api/' in script:
            print(f'\nScript #{i} contains API calls:')
            print(script[:500])

print('\n' + '='*60 + '\n')

print('=== Deep analysis of dlpanda.com ===\n')

r2 = session.get('https://dlpanda.com/zh-CN', 
                 headers={'User-Agent': UA},
                 impersonate='chrome120',
                 timeout=15)

if r2.status_code == 200:
    html = r2.text
    
    js_files = re.findall(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', html)
    print(f'JavaScript files: {js_files[:10]}')
    
    inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    print(f'\nInline scripts found: {len(inline_scripts)}')
    
    for i, script in enumerate(inline_scripts):
        if 'fetch' in script or 'ajax' in script or '/api/' in script:
            print(f'\nScript #{i} contains API calls:')
            print(script[:500])
