import sys
from curl_cffi import requests
import json

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

session = requests.Session()

print('=== Testing ttget.net API ===\n')

# Test /info endpoint
print('1. Testing /info endpoint')
r1 = session.post('https://ttget.net/info', 
                  data={'url': url},
                  headers={'User-Agent': UA, 'Referer': 'https://ttget.net/'},
                  impersonate='chrome120',
                  timeout=15)
print(f'Status: {r1.status_code}')
if r1.status_code == 200:
    print(f'Response: {r1.text[:1000]}')
    try:
        data = r1.json()
        print(f'JSON keys: {list(data.keys())}')
        if 'video' in data or 'url' in data:
            print('✅ Found video data!')
    except:
        print('Not JSON')

print('\n' + '='*60 + '\n')

print('=== Testing qload.info API ===\n')

# Test /download endpoint
print('1. Testing /download endpoint')
r2 = session.post('https://qload.info/download', 
                  data={'url': url},
                  headers={'User-Agent': UA, 'Referer': 'https://qload.info/'},
                  impersonate='chrome120',
                  timeout=15)
print(f'Status: {r2.status_code}')
if r2.status_code == 200:
    print(f'Response: {r2.text[:1000]}')
    try:
        data = r2.json()
        print(f'JSON keys: {list(data.keys())}')
        if 'video' in data or 'url' in data or 'download' in data:
            print('✅ Found video data!')
    except:
        print('Not JSON, checking for links')
        import re
        links = re.findall(r'href=["\']([^"\']+)["\']', r2.text)
        video_links = [l for l in links if 'video' in l.lower() or 'mp4' in l.lower() or 'download' in l.lower()]
        print(f'Video-related links: {video_links[:5]}')

print('\n' + '='*60 + '\n')

print('=== Testing tikmate.app API ===\n')

# Test /api/lookup endpoint
print('1. Testing https://api.tikmate.app/api/lookup')
r3 = session.post('https://api.tikmate.app/api/lookup', 
                  data={'url': url},
                  headers={'User-Agent': UA, 'Referer': 'https://tikmate.app/'},
                  impersonate='chrome120',
                  timeout=15)
print(f'Status: {r3.status_code}')
if r3.status_code == 200:
    print(f'Response: {r3.text[:1000]}')
    try:
        data = r3.json()
        print(f'JSON keys: {list(data.keys())}')
        if 'token' in data and 'id' in data:
            print('✅ Found token and id!')
            print(f'Download URL: https://tikmate.app/download/{data["token"]}/{data["id"]}.mp4')
            print(f'HD URL: https://tikmate.app/download/{data["token"]}/{data["id"]}.mp4?hd=1')
    except:
        print('Not JSON')
