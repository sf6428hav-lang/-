import httpx
import re
import json

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
url = 'https://v.douyin.com/1CzGfFJVQD0/'

# Test tikdownloader.io download endpoint
print('=== tikdownloader.io - full test ===')
r = httpx.post('https://tikdownloader.io/api/ajaxSearch', 
               data={'q': url, 'lang': 'en'},
               headers={'User-Agent': UA},
               timeout=15)
data = r.json()
html_content = data.get('data', '')
links = re.findall(r'https?://[^\s"\'<>]+', html_content)
video_links = [l for l in links if 'douyinvod' in l or ('video' in l.lower() and 'mp4' in l)]
print(f'Found {len(video_links)} video links')
if video_links:
    print(f'First video URL: {video_links[0]}')
    # Test if we can download
    try:
        r2 = httpx.get(video_links[0], headers={'User-Agent': UA}, timeout=10, follow_redirects=True)
        print(f'Download test: {r2.status_code}, size: {len(r2.content)} bytes')
    except Exception as e:
        print(f'Download error: {e}')

print()

# Test more services
services = [
    {
        'name': 'snaptik.app',
        'url': 'https://snaptik.app/api/v2/dl',
        'data': {'url': url}
    },
    {
        'name': 'tikmate.app',
        'url': 'https://tikmate.app/api/ajaxSearch',
        'data': {'q': url, 'lang': 'en'}
    },
    {
        'name': 'ttdownloader.com',
        'url': 'https://ttdownloader.com/search/',
        'data': {'url': url, 'format': '', 'token': 'test'}
    }
]

for svc in services:
    print(f"=== {svc['name']} ===")
    try:
        headers = {'User-Agent': UA}
        r = httpx.post(svc['url'], data=svc['data'], headers=headers, timeout=15, follow_redirects=True)
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            links = re.findall(r'https?://[^\s"\'<>]+', r.text)
            video_links = [l for l in links if 'douyinvod' in l or 'mp4' in l]
            print(f'Found {len(video_links)} video links')
            if video_links:
                print(f'First: {video_links[0][:100]}')
    except Exception as e:
        print(f'Error: {e}')
    print()
