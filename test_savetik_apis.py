import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

session = requests.Session()

# 测试 savetik.co 的 API
print('=== Testing savetik.co APIs ===\n')

# 1. ajaxSearch
print('1. Testing /api/ajaxSearch')
r1 = session.post('https://savetik.co/api/ajaxSearch', 
                  data={'q': url, 'lang': 'en'},
                  headers={'User-Agent': UA, 'Referer': 'https://savetik.co/'},
                  impersonate='chrome120',
                  timeout=15)
print(f'Status: {r1.status_code}')
if r1.status_code == 200:
    data1 = r1.json()
    print(f'Keys: {list(data1.keys())}')
    print(f'Response: {json.dumps(data1, indent=2, ensure_ascii=False)[:500]}')
    
    # 检查 data 字段
    if 'data' in data1:
        print(f'\nData field type: {type(data1["data"])}')
        if isinstance(data1['data'], dict):
            print(f'Data keys: {list(data1["data"].keys())}')
        elif isinstance(data1['data'], str):
            print(f'Data (str): {data1["data"][:300]}')

print('\n' + '='*60 + '\n')

# 2. tik-cdn.com convert API
print('2. Testing https://s3.tik-cdn.com/api/json/convert')
r2 = session.post('https://s3.tik-cdn.com/api/json/convert',
                  data={'url': url},
                  headers={'User-Agent': UA, 'Referer': 'https://savetik.co/'},
                  impersonate='chrome120',
                  timeout=15)
print(f'Status: {r2.status_code}')
if r2.status_code == 200:
    data2 = r2.json()
    print(f'Keys: {list(data2.keys())}')
    print(f'Response: {json.dumps(data2, indent=2, ensure_ascii=False)[:800]}')

print('\n' + '='*60 + '\n')

# 3. ajaxConvert/checkTask
print('3. Testing /api/ajaxConvert/checkTask')
r3 = session.post('https://savetik.co/api/ajaxConvert/checkTask',
                  data={'task_id': 'test'},
                  headers={'User-Agent': UA, 'Referer': 'https://savetik.co/'},
                  impersonate='chrome120',
                  timeout=15)
print(f'Status: {r3.status_code}')
if r3.status_code == 200:
    print(f'Response: {r3.text[:300]}')
