import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

session = requests.Session()

print('=== Deep testing ttget.net ===\n')

# Try different request formats
print('1. GET with query')
r1 = session.get('https://ttget.net/info?url=' + url, 
                 headers={'User-Agent': UA, 'Referer': 'https://ttget.net/'},
                 impersonate='chrome120',
                 timeout=15)
print(f'Status: {r1.status_code}')
if r1.status_code == 200:
    print(f'Response: {r1.text[:800]}')

print('\n2. POST with JSON')
r2 = session.post('https://ttget.net/info', 
                  json={'url': url},
                  headers={'User-Agent': UA, 'Referer': 'https://ttget.net/', 'Content-Type': 'application/json'},
                  impersonate='chrome120',
                  timeout=15)
print(f'Status: {r2.status_code}')
if r2.status_code == 200:
    print(f'Response: {r2.text[:800]}')

print('\n3. POST with form data (different field names)')
for field in ['url', 'link', 'video_url', 'q']:
    r3 = session.post('https://ttget.net/info', 
                      data={field: url},
                      headers={'User-Agent': UA, 'Referer': 'https://ttget.net/'},
                      impersonate='chrome120',
                      timeout=15)
    if r3.status_code == 200:
        print(f'Field "{field}" works! Status: {r3.status_code}')
        print(f'Response: {r3.text[:500]}')
        break

print('\n' + '='*60 + '\n')

print('=== Deep testing qload.info ===\n')

# Try different endpoints and formats
endpoints = ['/download', '/api/download', '/parse', '/api/parse']
for endpoint in endpoints:
    r4 = session.post('https://qload.info' + endpoint, 
                      data={'url': url},
                      headers={'User-Agent': UA, 'Referer': 'https://qload.info/'},
                      impersonate='chrome120',
                      timeout=15)
    print(f'{endpoint}: Status {r4.status_code}')
    if r4.status_code == 200:
        print(f'Response: {r4.text[:500]}')
        break

print('\n' + '='*60 + '\n')

print('=== Deep testing tikmate.app ===\n')

# Try with different request formats
print('1. POST with JSON')
r5 = session.post('https://api.tikmate.app/api/lookup', 
                  json={'url': url},
                  headers={'User-Agent': UA, 'Referer': 'https://tikmate.app/', 'Content-Type': 'application/json'},
                  impersonate='chrome120',
                  timeout=15)
print(f'Status: {r5.status_code}')
if r5.status_code == 200:
    print(f'Response: {r5.text[:800]}')
else:
    print(f'Response: {r5.text[:300]}')

print('\n2. POST with form data')
r6 = session.post('https://api.tikmate.app/api/lookup', 
                  data={'url': url},
                  headers={'User-Agent': UA, 'Referer': 'https://tikmate.app/'},
                  impersonate='chrome120',
                  timeout=15)
print(f'Status: {r6.status_code}')
if r6.status_code == 200:
    print(f'Response: {r6.text[:800]}')
else:
    print(f'Response: {r6.text[:300]}')
