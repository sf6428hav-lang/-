import httpx, re, sys
sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
url = 'https://v.douyin.com/1CzGfFJVQD0/'

# More services - batch 3
services = [
    {'name': 'musicallydown.com', 'url': 'https://musicallydown.com/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
    {'name': 'tikdown.app', 'url': 'https://tikdown.app/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
    {'name': 'tiktokdownload.com', 'url': 'https://tiktokdownload.com/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
    {'name': 'snaptik.to', 'url': 'https://snaptik.to/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
    {'name': 'tiktokvid.net', 'url': 'https://tiktokvid.net/api/ajaxSearch', 'data': {'q': url, 'lang': 'en'}},
    {'name': 'tikwm.app', 'url': 'https://tikwm.app/api/', 'data': {'url': url, 'hd': 1}},
]

for svc in services:
    print(f"=== {svc['name']} ===")
    try:
        headers = {'User-Agent': UA, 'Referer': 'https://' + svc['name'] + '/'}
        r = httpx.post(svc['url'], data=svc['data'], headers=headers, timeout=15, follow_redirects=True)
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            try:
                data = r.json()
                print(f'JSON keys: {list(data.keys())[:5]}')
                text = str(data)
            except:
                text = r.text
            video_urls = re.findall(r'https?://[^"\'\\s,<>]+', text)
            vlinks = [l for l in video_urls if 'douyinvod' in l or 'douyinpic' in l or ('video' in l.lower() and ('mp4' in l or 'm3u8' in l)) or 'zjcdn' in l or 'bytedance' in l or 'tiktok' in l]
            if vlinks:
                print(f'VIDEO FOUND: {len(vlinks)} links')
                print(f'  {vlinks[0][:180]}')
            else:
                print(f'  Total URLs: {len(video_urls)}, no video links')
        else:
            print(f'Failed: {r.text[:100]}')
    except Exception as e:
        print(f'Error: {str(e)[:100]}')
    print()
