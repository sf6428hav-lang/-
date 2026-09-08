import sys
from curl_cffi import requests
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

SERVICES = [
    {
        'name': 'savetik.co',
        'url': 'https://savetik.co/api/ajaxSearch',
        'data': {'q': url, 'lang': 'en'},
    },
    {
        'name': 'tikdownloader.app',
        'url': 'https://tikdownloader.app/api/ajaxSearch',
        'data': {'q': url, 'lang': 'en'},
    },
    {
        'name': 'tikdownloader.io',
        'url': 'https://tikdownloader.io/api/ajaxSearch',
        'data': {'q': url, 'lang': 'en'},
    },
    {
        'name': 'tiksave.io',
        'url': 'https://tiksave.io/api/ajaxSearch',
        'data': {'q': url, 'lang': 'en'},
    },
    {
        'name': 'botvod.com',
        'url': 'https://www.botvod.com/api/info',
        'data': {'url': url},
        'json': True,
    },
]

print('=== Final validation of all 5 services ===\n')

results = {}

for svc in SERVICES:
    print(f'--- {svc["name"]} ---')
    session = requests.Session()
    
    try:
        headers = {'User-Agent': UA, 'Referer': svc['url'].rsplit('/', 1)[0] + '/'}
        
        if svc.get('json'):
            r = session.post(svc['url'], json=svc['data'], headers=headers, impersonate='chrome120', timeout=15)
        else:
            r = session.post(svc['url'], data=svc['data'], headers=headers, impersonate='chrome120', timeout=15)
        
        print(f'Status: {r.status_code}')
        
        if r.status_code == 200:
            text = r.text
            
            # Find video CDN links
            all_urls = re.findall(r'https?://[^"\'<>\s&]+', text.replace('&amp;', '&'))
            video_cdn = [u for u in all_urls if 'zjcdn' in u or 'douyinvod' in u or 'bytedance' in u or 'byteicdn' in u]
            
            if video_cdn:
                print(f'✅ Found {len(video_cdn)} video CDN links')
                print(f'   First: {video_cdn[0][:120]}...')
                results[svc['name']] = video_cdn[0]
            else:
                # For botvod, check direct JSON
                try:
                    data = r.json()
                    if 'url' in data:
                        print(f'✅ Direct URL: {data["url"][:120]}...')
                        results[svc['name']] = data['url']
                    elif 'data' in data and isinstance(data['data'], dict) and 'url' in data['data']:
                        print(f'✅ Direct URL: {data["data"]["url"][:120]}...')
                        results[svc['name']] = data['data']['url']
                    else:
                        print(f'❌ No video URL in JSON')
                        results[svc['name']] = None
                except:
                    print(f'❌ No video CDN links found')
                    results[svc['name']] = None
        else:
            print(f'❌ Failed: {r.text[:100]}')
            results[svc['name']] = None
    except Exception as e:
        print(f'❌ Error: {str(e)[:100]}')
        results[svc['name']] = None
    
    print()

print('\n=== Summary ===')
for name, url in results.items():
    status = '✅' if url else '❌'
    print(f'{status} {name}')

working = sum(1 for v in results.values() if v)
print(f'\nWorking: {working} / {len(SERVICES)}')
