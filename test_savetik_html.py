import sys
from curl_cffi import requests
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

print('=== Testing savetik.co HTML parsing ===\n')

session = requests.Session()

r = session.post('https://savetik.co/api/ajaxSearch',
                data={'q': url, 'lang': 'en'},
                headers={'User-Agent': UA, 'Referer': 'https://savetik.co/'},
                impersonate='chrome120',
                timeout=15)

if r.status_code == 200:
    data = r.json()
    print(f'Response keys: {list(data.keys())}')
    
    if 'data' in data:
        html_content = data['data']
        print(f'HTML content length: {len(html_content)}')
        
        # Extract all URLs
        all_urls = re.findall(r'https?://[^"\'<>\s&]+', html_content.replace('&amp;', '&'))
        
        # Filter for video URLs
        video_urls = [u for u in all_urls if 'zjcdn' in u or 'douyinvod' in u or 'bytedance' in u or 'byteicdn' in u]
        
        print(f'\nTotal URLs: {len(all_urls)}')
        print(f'Video URLs: {len(video_urls)}')
        
        if video_urls:
            print(f'\n✅ Found {len(video_urls)} video URLs')
            for i, vurl in enumerate(video_urls[:5]):
                print(f'{i+1}. {vurl}')
        else:
            print('\nAll URLs found:')
            for i, u in enumerate(all_urls[:20]):
                print(f'{i+1}. {u}')
