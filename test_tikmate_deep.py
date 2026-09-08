import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# 测试不同格式的链接
test_urls = [
    'https://v.douyin.com/1CzGfFJVQD0/',
    'https://www.douyin.com/video/7308765981834234163',
    'https://v.douyin.com/iRNBho5u/',
]

print('=== Testing tikmate.app with different URL formats ===\n')

for url in test_urls:
    print(f'Testing: {url}')
    
    session = requests.Session()
    
    # 先获取主页看看有没有 token
    r_home = session.get('https://tikmate.app/', 
                         headers={'User-Agent': UA},
                         impersonate='chrome120',
                         timeout=15)
    
    # 检查是否有 token 或 CSRF
    if r_home.status_code == 200:
        html = r_home.text
        # 查找 token
        tokens = re.findall(r'name=["\']_token["\'][^>]+value=["\']([^"\']+)["\']', html)
        tokens += re.findall(r'name=["\']csrf[_-]?token["\'][^>]+value=["\']([^"\']+)["\']', html)
        
        if tokens:
            print(f'Found token: {tokens[0][:50]}...')
            
            # 尝试带 token 请求
            r = session.post('https://api.tikmate.app/api/lookup', 
                             json={'url': url, 'token': tokens[0]},
                             headers={'User-Agent': UA, 'Referer': 'https://tikmate.app/', 'Content-Type': 'application/json'},
                             impersonate='chrome120',
                             timeout=15)
            print(f'With token - Status: {r.status_code}')
            if r.status_code == 200:
                data = r.json()
                print(f'Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}')
                if data.get('success'):
                    print('✅ SUCCESS!')
                    break
            else:
                print(f'Response: {r.text[:200]}')
        else:
            print('No token found on homepage')
    
    # 尝试直接请求
    r = session.post('https://api.tikmate.app/api/lookup', 
                     json={'url': url},
                     headers={'User-Agent': UA, 'Referer': 'https://tikmate.app/', 'Content-Type': 'application/json'},
                     impersonate='chrome120',
                     timeout=15)
    print(f'Direct request - Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(f'Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}')
        if data.get('success'):
            print('✅ SUCCESS!')
            break
    else:
        print(f'Response: {r.text[:200]}')
    
    print()
