import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

print('=== Deep testing snaptik.life form submission ===\n')

session = requests.Session()

# 获取主页找表单
r_home = session.get('https://snaptik.life/',
                     headers={'User-Agent': UA},
                     impersonate='chrome120',
                     timeout=10)

if r_home.status_code == 200:
    html = r_home.text
    
    # 查找所有 script 标签中的 fetch/ajax 调用
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    
    print(f'Found {len(scripts)} script tags')
    
    for i, script in enumerate(scripts):
        if 'fetch' in script or 'ajax' in script or 'XMLHttpRequest' in script:
            print(f'\nScript #{i} has fetch/ajax calls:')
            # 提取 URL
            fetch_urls = re.findall(r'fetch\s*\(\s*["\']([^"\']+)["\']', script)
            ajax_urls = re.findall(r'\.ajax\s*\(\s*["\']([^"\']+)["\']', script)
            xhr_urls = re.findall(r'\.open\s*\(\s*["\'](?:POST|GET)["\']\s*,\s*["\']([^"\']+)["\']', script)
            
            if fetch_urls:
                print(f'  Fetch URLs: {fetch_urls[:10]}')
            if ajax_urls:
                print(f'  Ajax URLs: {ajax_urls[:10]}')
            if xhr_urls:
                print(f'  XHR URLs: {xhr_urls[:10]}')
            
            # 打印关键代码片段
            lines = script.split('\n')
            for line in lines:
                if 'fetch' in line or 'ajax' in line or '/api/' in line or 'post' in line.lower():
                    print(f'  {line.strip()[:150]}')

print('\n\n=== Testing tiktokdownload.online ===\n')

session2 = requests.Session()

r_home2 = session2.get('https://tiktokdownload.online/',
                      headers={'User-Agent': UA},
                      impersonate='chrome120',
                      timeout=10)

if r_home2.status_code == 200:
    html2 = r_home2.text
    
    # 查找所有 script 标签中的 fetch/ajax 调用
    scripts2 = re.findall(r'<script[^>]*>(.*?)</script>', html2, re.DOTALL)
    
    print(f'Found {len(scripts2)} script tags')
    
    for i, script in enumerate(scripts2):
        if 'fetch' in script or 'ajax' in script or 'XMLHttpRequest' in script:
            print(f'\nScript #{i} has fetch/ajax calls:')
            fetch_urls = re.findall(r'fetch\s*\(\s*["\']([^"\']+)["\']', script)
            ajax_urls = re.findall(r'\.ajax\s*\(\s*["\']([^"\']+)["\']', script)
            xhr_urls = re.findall(r'\.open\s*\(\s*["\'](?:POST|GET)["\']\s*,\s*["\']([^"\']+)["\']', script)
            
            if fetch_urls:
                print(f'  Fetch URLs: {fetch_urls[:10]}')
            if ajax_urls:
                print(f'  Ajax URLs: {ajax_urls[:10]}')
            if xhr_urls:
                print(f'  XHR URLs: {xhr_urls[:10]}')
            
            lines = script.split('\n')
            for line in lines:
                if 'fetch' in line or 'ajax' in line or '/api/' in line or 'post' in line.lower():
                    print(f'  {line.strip()[:150]}')

print('\n\n=== Testing easydown.vip with different SSL ===\n')

session3 = requests.Session()

try:
    r_home3 = session3.get('https://easydown.vip/',
                          headers={'User-Agent': UA},
                          impersonate='chrome119',  # 尝试不同的浏览器指纹
                          timeout=10)
    
    print(f'Status: {r_home3.status_code}')
    
    if r_home3.status_code == 200:
        html3 = r_home3.text
        
        scripts3 = re.findall(r'<script[^>]*>(.*?)</script>', html3, re.DOTALL)
        print(f'Found {len(scripts3)} script tags')
        
        for i, script in enumerate(scripts3):
            if 'fetch' in script or 'ajax' in script:
                print(f'\nScript #{i} has fetch/ajax:')
                fetch_urls = re.findall(r'fetch\s*\(\s*["\']([^"\']+)["\']', script)
                if fetch_urls:
                    print(f'  Fetch URLs: {fetch_urls[:10]}')
except Exception as e:
    print(f'Error: {str(e)[:150]}')
