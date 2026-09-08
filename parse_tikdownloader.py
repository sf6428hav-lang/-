import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

print('=== Parsing tikdownloader.app response ===\n')

session = requests.Session()

r = session.post('https://tikdownloader.app/api/ajaxSearch', 
                data={'q': url, 'lang': 'en'},
                headers={'User-Agent': UA, 'Referer': 'https://tikdownloader.app/'},
                impersonate='chrome120',
                timeout=15)

if r.status_code == 200:
    data = r.json()
    html_data = data.get('data', '')
    
    print(f'HTML data length: {len(html_data)} chars')
    
    # 提取所有链接
    all_links = re.findall(r'href=["\']([^"\']+)["\']', html_data)
    print(f'\nTotal links found: {len(all_links)}')
    
    # 过滤视频相关链接
    video_links = [l for l in all_links if 'download' in l.lower() or 'video' in l.lower() or 'mp4' in l.lower()]
    print(f'Video-related links: {len(video_links)}')
    
    for i, link in enumerate(video_links[:10]):
        print(f'{i+1}. {link}')
    
    # 提取所有 URL
    all_urls = re.findall(r'https?://[^"\'<>\s]+', html_data)
    print(f'\nAll URLs found: {len(all_urls)}')
    
    # 查找视频 CDN 链接
    cdn_links = [u for u in all_urls if 'douyinvod' in u or 'douyinpic' in u or 'zjcdn' in u or 'bytedance' in u]
    print(f'\nVideo CDN links: {len(cdn_links)}')
    for i, link in enumerate(cdn_links[:5]):
        print(f'{i+1}. {link[:150]}...')
    
    # 查找下载按钮
    download_btns = re.findall(r'<a[^>]*class=["\'][^"\']*download[^"\']*["\'][^>]*href=["\']([^"\']+)["\']', html_data)
    print(f'\nDownload buttons: {len(download_btns)}')
    for i, btn in enumerate(download_btns[:5]):
        print(f'{i+1}. {btn}')
