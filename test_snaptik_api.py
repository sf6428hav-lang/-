import sys
from curl_cffi import requests
import json

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

session = requests.Session()

print('=== Testing snaptik.app API ===\n')

# 1. Get token
print('1. Getting token from /api/token')
r1 = session.get('https://snaptik.app/api/token', 
                 headers={'User-Agent': UA, 'Referer': 'https://snaptik.app/'},
                 impersonate='chrome120',
                 timeout=15)
print(f'Status: {r1.status_code}')
print(f'Response: {r1.text[:500]}')

if r1.status_code == 200:
    try:
        token_data = r1.json()
        print(f'Token data: {token_data}')
        
        if 'token' in token_data:
            token = token_data['token']
            print(f'\nGot token: {token[:50]}...')
            
            # 2. Extract video
            print('\n2. Extracting video from /api/extract')
            extract_url = f'https://snaptik.app/api/extract?url={url}'
            r2 = session.get(extract_url,
                           headers={'User-Agent': UA, 'Referer': 'https://snaptik.app/', 'X-Token': token},
                           impersonate='chrome120',
                           timeout=15)
            print(f'Status: {r2.status_code}')
            print(f'Response: {r2.text[:1000]}')
            
            if r2.status_code == 200:
                try:
                    extract_data = r2.json()
                    print(f'\nExtract data keys: {list(extract_data.keys())}')
                    if 'data' in extract_data:
                        print(f'Data: {extract_data["data"]}')
                except Exception as e:
                    print(f'Failed to parse JSON: {e}')
    except Exception as e:
        print(f'Failed to parse token: {e}')
