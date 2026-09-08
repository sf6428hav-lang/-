import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

session = requests.Session()

print('=== Analyzing ssstik.io JavaScript ===\n')

# Fetch the main JS file
print('Fetching /js/script_ssstik.min.js')
r_js = session.get('https://ssstik.io/js/script_ssstik.min.js?v=2026sep03.1', 
                   headers={'User-Agent': UA},
                   impersonate='chrome120',
                   timeout=15)

if r_js.status_code == 200:
    js_content = r_js.text
    print(f'JS file size: {len(js_content)} chars')
    
    # Look for API endpoints
    api_endpoints = re.findall(r'["\']([^"\']*(?:/api/|/ajax|/parse|/download|/extract)[^"\']*)["\']', js_content)
    print(f'\nAPI endpoints found: {len(api_endpoints)}')
    for endpoint in api_endpoints[:20]:
        print(f'  - {endpoint}')
    
    # Look for fetch/ajax calls
    fetch_patterns = [
        r'fetch\s*\(\s*["\']([^"\']+)["\']',
        r'\.ajax\s*\(\s*\{[^}]*url:\s*["\']([^"\']+)["\']',
        r'\.post\s*\(\s*["\']([^"\']+)["\']',
        r'\.get\s*\(\s*["\']([^"\']+)["\']'
    ]
    
    for pattern in fetch_patterns:
        matches = re.findall(pattern, js_content)
        if matches:
            print(f'\nPattern "{pattern[:30]}..." found:')
            for match in matches[:10]:
                print(f'  - {match}')

print('\n' + '='*60 + '\n')

print('=== Analyzing dlpanda.com JavaScript ===\n')

# Fetch the main JS file
print('Fetching app-E5aetN4P.js')
r_js2 = session.get('https://dlpanda.com/build/assets/app-E5aetN4P.js', 
                    headers={'User-Agent': UA},
                    impersonate='chrome120',
                    timeout=15)

if r_js2.status_code == 200:
    js_content2 = r_js2.text
    print(f'JS file size: {len(js_content2)} chars')
    
    # Look for API endpoints
    api_endpoints2 = re.findall(r'["\']([^"\']*(?:/api/|/ajax|/parse|/download|/extract)[^"\']*)["\']', js_content2)
    print(f'\nAPI endpoints found: {len(api_endpoints2)}')
    for endpoint in api_endpoints2[:20]:
        print(f'  - {endpoint}')
    
    # Look for fetch/ajax calls
    for pattern in fetch_patterns:
        matches = re.findall(pattern, js_content2)
        if matches:
            print(f'\nPattern "{pattern[:30]}..." found:')
            for match in matches[:10]:
                print(f'  - {match}')
