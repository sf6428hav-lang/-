import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

print('=== Testing tiktokdownloader.online ===\n')

session = requests.Session()

# 尝试它的API端点
api_url = 'https://www.tikwm.com/api/'
r = session.post(api_url,
                data={'url': url, 'hd': 1},
                headers={'User-Agent': UA, 'Referer': 'https://tiktokdownloader.online/'},
                impersonate='chrome120',
                timeout=15)

print(f'Status: {r.status_code}')

if r.status_code == 200:
    try:
        data = r.json()
        print(f'Response keys: {list(data.keys())}')
        
        if 'data' in data:
            data_content = data['data']
            if isinstance(data_content, dict):
                print(f'Data keys: {list(data_content.keys())}')
                
                if 'play' in data_content:
                    print(f'✅ Video URL: {data_content["play"]}')
                elif 'url' in data_content:
                    print(f'✅ URL: {data_content["url"]}')
    except Exception as e:
        print(f'Error: {str(e)[:100]}')
else:
    print(f'Failed: {r.text[:200]}')
