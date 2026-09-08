import httpx
import re
import json

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
url = 'https://v.douyin.com/1CzGfFJVQD0/'

# Test more services
services = [
    {
        'name': 'douyindownload.com',
        'url': 'https://douyindownload.com/api',
        'data': {'url': url}
    },
    {
        'name': 'tikdown.org',
        'url': 'https://tikdown.org/api',
        'data': {'url': url}
    },
    {
        'name': 'snaptik.dev',
        'url': 'https://snaptik.dev/api',
        'data': {'url': url}
    },
    {
        'name': 'tiktokdownloader.app',
        'url': 'https://tiktokdownloader.app/api',
        'data': {'url': url}
    }
]

for svc in services:
    print(f"=== {svc['name']} ===")
    try:
        headers = {'User-Agent': UA}
        r = httpx.post(svc['url'], data=svc['data'], headers=headers, timeout=15, follow_redirects=True)
        
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            # Try to parse as JSON
            try:
                data = r.json()
                print(f'Response keys: {list(data.keys())[:5]}')
                if 'data' in data:
                    print(f'Data: {str(data["data"])[:200]}')
            except:
                # Try to find URLs in HTML
                links = re.findall(r'https?://[^\s"\'<>]+', r.text)
                video_links = [l for l in links if 'douyinvod' in l or 'video' in l.lower() or 'mp4' in l]
                print(f'Found {len(video_links)} video links')
                if video_links:
                    print(f'First: {video_links[0][:150]}')
    except Exception as e:
        print(f'Error: {e}')
    print()
