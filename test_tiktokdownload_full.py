import sys
from curl_cffi import requests
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

print('=== Testing tiktokdownload.online /abc endpoint ===\n')

session = requests.Session()

# First visit homepage to get cookies
r_home = session.get('https://tiktokdownload.online/',
                    headers={'User-Agent': UA},
                    impersonate='chrome120',
                    timeout=15)

print(f'Homepage status: {r_home.status_code}')
print(f'Cookies: {len(session.cookies)}')

# Try POST /abc?url=dl
r = session.post('https://tiktokdownload.online/abc?url=dl',
                data={'id': url, 'locale': 'en'},
                headers={'User-Agent': UA, 'Referer': 'https://tiktokdownload.online/'},
                impersonate='chrome120',
                timeout=15)

print(f'\nAPI Status: {r.status_code}')
print(f'Content-Length: {len(r.content)} bytes')
print(f'Content-Type: {r.headers.get("content-type", "unknown")}')

# Save to file
with open('tiktokdownload_response.html', 'wb') as f:
    f.write(r.content)

print(f'\nSaved response to tiktokdownload_response.html')

if r.status_code == 200:
    text = r.text
    
    # Look for video URLs
    all_urls = re.findall(r'https?://[^"\'<>\s]+', text)
    video_urls = [u for u in all_urls if 'douyinvod' in u or 'bytedance' in u or 'zjcdn' in u or 'douyin' in u.lower() or 'mp4' in u.lower() or 'video' in u.lower()]
    
    print(f'\nTotal URLs found: {len(all_urls)}')
    print(f'Video-related URLs: {len(video_urls)}')
    
    if video_urls:
        print('\n✅ Found video URLs!')
        for i, vurl in enumerate(video_urls[:10]):
            print(f'  {i+1}. {vurl[:150]}')
    else:
        print('\nNo video URLs found')
        print(f'\nFirst 2000 chars of response:')
        print(text[:2000])
