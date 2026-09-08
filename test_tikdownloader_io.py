import sys
from curl_cffi import requests
import json
import re
import time

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

print('=== Testing tikdownloader.io API flow ===\n')

session = requests.Session()

# Step 1: ajaxSearch
print('Step 1: /api/ajaxSearch')
r1 = session.post('https://tikdownloader.io/api/ajaxSearch',
                 data={'q': url, 'lang': 'en'},
                 headers={'User-Agent': UA, 'Referer': 'https://tikdownloader.io/'},
                 impersonate='chrome120',
                 timeout=15)

print(f'Status: {r1.status_code}')

if r1.status_code == 200:
    try:
        data1 = r1.json()
        print(f'Response keys: {list(data1.keys())}')
        
        if 'data' in data1:
            html_data = data1['data']
            print(f'HTML data length: {len(html_data)}')
            
            # 查找任务ID或token
            task_ids = re.findall(r'data-task-id=["\']([^"\']+)["\']', html_data)
            tokens = re.findall(r'data-token=["\']([^"\']+)["\']', html_data)
            
            print(f'Task IDs: {task_ids[:3]}')
            print(f'Tokens: {tokens[:3]}')
            
            # 查找视频链接
            video_urls = re.findall(r'https?://[^"\'<>\s]+', html_data)
            video_cdn = [u for u in video_urls if 'douyinvod' in u or 'douyinpic' in u or 'zjcdn' in u or 'bytedance' in u]
            
            print(f'\nVideo CDN links found: {len(video_cdn)}')
            for i, vurl in enumerate(video_cdn[:5]):
                print(f'{i+1}. {vurl[:100]}...')
            
            # Step 2: 如果有任务ID，检查任务状态
            if task_ids:
                print(f'\nStep 2: /api/ajaxConvert/checkTask')
                r2 = session.post('https://tikdownloader.io/api/ajaxConvert/checkTask',
                                 data={'task_id': task_ids[0]},
                                 headers={'User-Agent': UA, 'Referer': 'https://tikdownloader.io/'},
                                 impersonate='chrome120',
                                 timeout=15)
                
                print(f'Status: {r2.status_code}')
                if r2.status_code == 200:
                    print(f'Response: {r2.text[:500]}')
            
            # Step 3: 尝试 convert API
            print(f'\nStep 3: https://s3.tik-cdn.com/api/json/convert')
            r3 = session.post('https://s3.tik-cdn.com/api/json/convert',
                             data={'url': url},
                             headers={'User-Agent': UA, 'Referer': 'https://tikdownloader.io/'},
                             impersonate='chrome120',
                             timeout=15)
            
            print(f'Status: {r3.status_code}')
            if r3.status_code == 200:
                try:
                    data3 = r3.json()
                    print(f'Response: {json.dumps(data3, indent=2, ensure_ascii=False)[:800]}')
                except:
                    print(f'Response: {r3.text[:500]}')
    except Exception as e:
        print(f'Error parsing response: {str(e)[:100]}')
else:
    print(f'Failed: {r1.text[:200]}')
