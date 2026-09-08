import httpx
import re
import json

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
url = 'https://v.douyin.com/1CzGfFJVQD0/'

# Test more services
services = [
    {
        'name': 'ssstik.io',
        'url': 'https://ssstik.io/abc?url=' + url,
        'method': 'GET'
    },
    {
        'name': 'savetik.net',
        'url': 'https://savetik.net/api/ajaxSearch',
        'data': {'q': url, 'lang': 'en'}
    },
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
        'name': 'musicaldown.com',
        'url': 'https://musicaldown.com/id',
        'method': 'GET'
    }
]

for svc in services:
    print(f"=== {svc['name']} ===")
    try:
        headers = {'User-Agent': UA, 'Referer': svc['url'].rsplit('/', 1)[0]}
        if svc.get('method') == 'GET':
            r = httpx.get(svc['url'], headers=headers, timeout=15, follow_redirects=True)
        else:
            r = httpx.post(svc['url'], data=svc['data'], headers=headers, timeout=15, follow_redirects=True)
        
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            links = re.findall(r'https?://[^\s"\'<>]+', r.text)
            video_links = [l for l in links if 'douyinvod' in l or 'video' in l.lower() or 'mp4' in l]
            print(f'Found {len(video_links)} video links')
            if video_links:
                print(f'First: {video_links[0][:150]}')
    except Exception as e:
        print(f'Error: {e}')
    print()
