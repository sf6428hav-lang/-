import sys
from curl_cffi import requests
import json

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

session = requests.Session()

print('=== Testing ssstik.io API ===\n')

# 访问主页
print('1. Visiting homepage')
r1 = session.get('https://ssstik.io/', 
                 headers={'User-Agent': UA, 'Referer': 'https://ssstik.io/'},
                 impersonate='chrome120',
                 timeout=15)
print(f'Status: {r1.status_code}')

if r1.status_code == 200:
    html = r1.text
    print(f'HTML length: {len(html)} chars')
    
    # 查找表单和 API
    import re
    forms = re.findall(r'<form[^>]*action=["\']([^"\']+)["\'][^>]*>', html)
    apis = re.findall(r'["\']([^"\']*(?:/api/|/ajax|/parse|/download)[^"\']*)["\']', html)
    
    print(f'Forms found: {forms}')
    print(f'API endpoints: {apis[:10]}')
    
    # 尝试找到 CSRF token
    csrf = re.findall(r'name=["\']_token["\'][^>]+value=["\']([^"\']+)["\']', html)
    csrf += re.findall(r'name=["\']csrf[_-]?token["\'][^>]+value=["\']([^"\']+)["\']', html)
    
    if csrf:
        print(f'CSRF token: {csrf[0][:50]}...')

print('\n' + '='*60 + '\n')

print('=== Testing dlpanda.com API ===\n')

# 访问主页
print('1. Visiting homepage')
r2 = session.get('https://dlpanda.com/zh-CN', 
                 headers={'User-Agent': UA, 'Referer': 'https://dlpanda.com/'},
                 impersonate='chrome120',
                 timeout=15)
print(f'Status: {r2.status_code}')

if r2.status_code == 200:
    html = r2.text
    print(f'HTML length: {len(html)} chars')
    
    forms = re.findall(r'<form[^>]*action=["\']([^"\']+)["\'][^>]*>', html)
    apis = re.findall(r'["\']([^"\']*(?:/api/|/ajax|/parse|/download)[^"\']*)["\']', html)
    fetch_calls = re.findall(r'fetch\s*\(\s*["\']([^"\']+)["\']', html)
    
    print(f'Forms found: {forms}')
    print(f'API endpoints: {apis[:10]}')
    print(f'Fetch calls: {fetch_calls[:10]}')
    
    csrf = re.findall(r'name=["\']_token["\'][^>]+value=["\']([^"\']+)["\']', html)
    csrf += re.findall(r'name=["\']csrf[_-]?token["\'][^>]+value=["\']([^"\']+)["\']', html)
    
    if csrf:
        print(f'CSRF token: {csrf[0][:50]}...')
