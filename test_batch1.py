import httpx, re, sys
sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
url = 'https://v.douyin.com/1CzGfFJVQD0/'

# Batch 1 - more services to test
services = [
    {'name': 'cobalt.tools', 'url': 'https://cobalt.tools/api/json', 'data': {'url': url, 'vCodec': 'h264', 'vQuality': '720'}, 'json': True},
    {'name': 'dlpanda.com', 'url': 'https://dlpanda.com/api/ajaxSearch', 'data': {'url': url, 'lang': 'en'}},
    {'name': 'tiklydown.com', 'url': 'https://tiklydown.com/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
    {'name': 'snaptik.cc', 'url': 'https://snaptik.cc/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
    {'name': 'tikfull.com', 'url': 'https://tikfull.com/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
    {'name': 'tikdownloader.app', 'url': 'https://tikdownloader.app/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
]

for svc in services:
    print(f"=== {svc['name']} ===")
    try:
        headers = {'User-Agent': UA, 'Referer': 'https://' + svc['name'] + '/'}
        if svc.get('json'):
            r = httpx.post(svc['url'], json=svc['data'], headers={**headers, 'Content-Type': 'application/json'}, timeout=15, follow_redirects=True)
        else:
            r = httpx.post(svc['url'], data=svc['data'], headers=headers, timeout=15, follow_redirects=True)
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            try:
                data = r.json()
                print(f'JSON keys: {list(data.keys())[:5]}')
                # Search for video URLs
                text = str(data)
                video_urls = re.findall(r'https?://[^"\'\\s,]+', text)
                vlinks = [l for l in video_urls if 'douyinvod' in l or 'douyinpic' in l or ('video' in l.lower() and ('mp4' in l or 'm3u8' in l))]
                if vlinks:
                    print(f'VIDEO FOUND: {len(vlinks)} links')
                    print(f'  {vlinks[0][:150]}')
                else:
                    print(f'  Total URLs: {len(video_urls)}, sample: {video_urls[:2]}')
            except:
                text = r.text
                video_urls = re.findall(r'https?://[^"\'\\s,<>]+', text)
                vlinks = [l for l in video_urls if 'douyinvod' in l or 'douyinpic' in l or ('video' in l.lower() and ('mp4' in l or 'm3u8' in l))]
                print(f'Found {len(vlinks)} video links in HTML')
        else:
            print(f'Failed: {r.text[:200]}')
    except Exception as e:
        print(f'Error: {e}')
    print()
