import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

print('=== Testing tiktokdownload.online /abc endpoint ===\n')

session = requests.Session()

# Try POST /abc?url=dl
r = session.post('https://tiktokdownload.online/abc?url=dl',
                data={'id': url, 'locale': 'en'},
                headers={'User-Agent': UA, 'Referer': 'https://tiktokdownload.online/'},
                impersonate='chrome120',
                timeout=15)

print(f'Status: {r.status_code}')
print(f'Content-Type: {r.headers.get("content-type", "unknown")}')

if r.status_code == 200:
    # Check JSON
    try:
        data = r.json()
        print(f'\n✅ JSON response')
        print(f'Keys: {list(data.keys())[:10]}')
        print(f'\n完整响应:')
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
    except:
        print(f'\nHTML response')
        print(r.text[:1500])
        
        # Look for video URLs
        video_urls = re.findall(r'https?://[^"\'<>\s]+', r.text)
        video_cdn = [u for u in video_urls if 'douyinvod' in u or 'bytedance' in u or 'zjcdn' in u or 'douyin' in u.lower()]
        if video_cdn:
            print(f'\n✅ 找到 {len(video_cdn)} 个视频 URL!')
            for i, vurl in enumerate(video_cdn[:5]):
                print(f'  {i+1}. {vurl[:150]}')

print('\n' + '='*60)
