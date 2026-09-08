import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

services = [
    {'name': 'dlpanda.com', 'url': 'https://dlpanda.com/zh-CN'},
    {'name': 'snaptik.app', 'url': 'https://snaptik.app/'},
    {'name': 'ssstik.io', 'url': 'https://ssstik.io/'},
    {'name': 'savetik.co', 'url': 'https://savetik.co/'},
    {'name': 'tikmate.online', 'url': 'https://tikmate.online/'},
    {'name': 'godownloader.com', 'url': 'https://godownloader.com/douyin-downloader'},
]

print('=== 使用 curl_cffi 测试服务 ===')

for svc in services:
    print(f'=== {svc["name"]} ===')
    try:
        session = requests.Session()
        r = session.get(svc['url'], headers={'User-Agent': UA}, impersonate='chrome120', timeout=15)
        print(f'主页 Status: {r.status_code}')
        
        if r.status_code == 200:
            text = r.text
            api_urls = re.findall(r'["\'](/api/[^"\']+)["\']', text)
            fetch_urls = re.findall(r'fetch\s*\(\s*["\']([^"\']+)["\']', text)
            
            print(f'API URLs: {api_urls[:5]}')
            print(f'Fetch URLs: {fetch_urls[:3]}')
            
            common_apis = ['/api/ajaxSearch', '/api/download', '/api/parse']
            
            for api in common_apis:
                try:
                    api_url = api if api.startswith('http') else svc['url'].rstrip('/') + api
                    r2 = session.post(api_url, data={'url': url, 'lang': 'en'}, headers={'User-Agent': UA}, impersonate='chrome120', timeout=15)
                    if r2.status_code == 200:
                        try:
                            data = r2.json()
                            print(f'{api} 成功!')
                            text_data = str(data)
                            video_urls = re.findall(r'https?://[^"\'\\s,<>]+', text_data)
                            vlinks = [l for l in video_urls if 'douyinvod' in l or 'douyinpic' in l or ('video' in l.lower() and ('mp4' in l or 'm3u8' in l)) or 'zjcdn' in l or 'bytedance' in l or 'byteicdn' in l]
                            if vlinks:
                                print(f'视频找到: {len(vlinks)} 个链接')
                                print(f'  {vlinks[0][:150]}')
                                break
                        except:
                            pass
                except:
                    pass
        else:
            print(f'主页访问失败: {r.status_code}')
    except Exception as e:
        print(f'Error: {str(e)[:150]}')
    print()
