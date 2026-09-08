import httpx
import re

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
url = 'https://v.douyin.com/1CzGfFJVQD0/'

# tikdownloader - extract full video URL
print('=== tikdownloader.io - extract video URL ===')
r = httpx.post('https://tikdownloader.io/api/ajaxSearch', 
               data={'q': url, 'lang': 'en'},
               headers={'User-Agent': UA},
               timeout=15)
data = r.json()
html_content = data.get('data', '')
# Find all video URLs
links = re.findall(r'https?://[^\s"\'<>]+', html_content)
video_links = [l for l in links if 'douyinvod' in l or 'video' in l.lower()]
print(f'Found {len(video_links)} video links')
for l in video_links[:3]:
    print(f'  {l}')

print()

# Test more services
more = [
    {'name': 'snaptik.app', 'url': 'https://snaptik.app/api/v2/dl', 'data': {'url': url}},
    {'name': 'tikmate.app', 'url': 'https://tikmate.app/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
    {'name': 'ttdownloader.com', 'url': 'https://ttdownloader.com/search/', 'data': {'url': url, 'format': '', 'token': 'test'}},
]

for svc in more:
    print(f"=== {svc['name']} ===")
    try:
        headers = {'User-Agent': UA}
        r = httpx.post(svc['url'], data=svc['data'], headers=headers, timeout=15, allow_redirects=True)
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            # Try to find video URLs
            links = re.findall(r'https?://[^\s"\'<>]+', r.text)
            video_links = [l for l in links if 'douyinvod' in l or 'mp4' in l or 'video' in l.lower()]
            print(f'Found {len(video_links)} video links')
            for l in video_links[:2]:
                print(f'  {l[:100]}')
        else:
            print(f'Failed: {r.status_code}')
    except Exception as e:
        print(f'Error: {e}')
    print()

# Test musicaldown.com API
print('=== musicaldown.com ===')
try:
    # First get CSRF token
    r1 = httpx.get('https://musicaldown.com/id', headers={'User-Agent': UA}, timeout=15)
    # Extract token
    token_match = re.search(r'name="token" value="([^"]+)"', r1.text)
    if token_match:
        token = token_match.group(1)
        print(f'Token: {token}')
        r2 = httpx.post('https://musicaldown.com/id/download', 
                       data={'link': url, 'token': token},
                       headers={'User-Agent': UA, 'Referer': 'https://musicaldown.com/id'},
                       timeout=15)
        print(f'Status: {r2.status_code}')
        if r2.status_code == 200:
            links = re.findall(r'https?://[^\s"\'<>]+', r2.text)
            video_links = [l for l in links if 'douyinvod' in l or 'mp4' in l or 'video' in l.lower()]
            print(f'Found {len(video_links)} video links')
            for l in video_links[:2]:
                print(f'  {l[:100]}')
except Exception as e:
    print(f'Error: {e}')
