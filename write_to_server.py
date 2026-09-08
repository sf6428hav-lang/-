import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Write parser_douyin.py with rotation logic
parser_code = '''import asyncio
import re
from curl_cffi import requests as cffi_requests
from pathlib import Path
from ..config import settings
from .parser import ParseResult

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

SERVICES = [
    {
        'name': 'tiksave.io',
        'url': 'https://tiksave.io/api/ajaxSearch',
        'data_fn': lambda u: {'q': u, 'lang': 'en'},
        'parse_fn': '_parse_ajaxSearch_html',
    },
    {
        'name': 'tikdownloader.io',
        'url': 'https://tikdownloader.io/api/ajaxSearch',
        'data_fn': lambda u: {'q': u, 'lang': 'en'},
        'parse_fn': '_parse_ajaxSearch_html',
    },
    {
        'name': 'tikdownloader.app',
        'url': 'https://tikdownloader.app/api/ajaxSearch',
        'data_fn': lambda u: {'q': u, 'lang': 'en'},
        'parse_fn': '_parse_ajaxSearch_html',
    },
    {
        'name': 'savetik.co',
        'url': 'https://savetik.co/api/ajaxSearch',
        'data_fn': lambda u: {'q': u, 'lang': 'en'},
        'parse_fn': '_parse_ajaxSearch_html',
    },
    {
        'name': 'botvod.com',
        'url': 'https://www.botvod.com/api/info',
        'data_fn': lambda u: {'url': u},
        'parse_fn': '_parse_botvod',
    },
]

def _extract_video_url_from_html(html_text):
    """从ajaxSearch返回的HTML中提取视频CDN链接"""
    all_urls = re.findall(r'https?://[^"\\'<>\\s&]+', html_text.replace('&amp;', '&'))
    video_cdn = [u for u in all_urls if 'zjcdn' in u or 'douyinvod' in u or 'bytedance' in u or 'byteicdn' in u]
    return video_cdn[0] if video_cdn else None

def _parse_ajaxSearch_html(resp):
    """解析ajaxSearch类服务的JSON+HTML响应"""
    data = resp.json()
    html_content = data.get('data', '')
    return _extract_video_url_from_html(html_content)

def _parse_botvod(resp):
    """解析botvod.com的纯JSON响应"""
    data = resp.json()
    if 'url' in data:
        return data['url']
    if 'data' in data and isinstance(data['data'], dict):
        return data['data'].get('url')
    return None

async def parse_douyin(url: str) -> ParseResult:
    """解析抖音视频，支持5个服务的轮询容错"""
    
    for svc in SERVICES:
        try:
            session = cffi_requests.Session()
            headers = {'User-Agent': UA, 'Referer': svc['url'].rsplit('/', 1)[0] + '/'}
            
            # botvod用JSON，其他用form data
            if svc['name'] == 'botvod.com':
                resp = session.post(svc['url'], json=svc['data_fn'](url), headers=headers, impersonate='chrome120', timeout=20)
            else:
                resp = session.post(svc['url'], data=svc['data_fn'](url), headers=headers, impersonate='chrome120', timeout=20)
            
            if resp.status_code == 200:
                parse_fn = globals()[svc['parse_fn']]
                video_url = parse_fn(resp)
                
                if video_url:
                    print(f"[{svc['name']}] ✅ 成功获取视频链接")
                    return ParseResult(
                        platform='douyin',
                        video_url=video_url,
                        title='',
                        metadata={'service': svc['name']}
                    )
                else:
                    print(f"[{svc['name']}] ⚠️ 响应中未找到视频链接，尝试下一个服务")
            else:
                print(f"[{svc['name']}] ❌ HTTP {resp.status_code}，尝试下一个服务")
        except Exception as e:
            print(f"[{svc['name']}] ❌ 错误: {str(e)[:80]}，尝试下一个服务")
    
    # 所有服务都失败
    raise ValueError("所有抖音下载服务均不可用，请稍后重试")
'''

# Write to server
stdin, stdout, stderr = ssh.exec_command('cat > /opt/douyin-script/backend/app/services/parser_douyin.py << "ENDOFFILE"\n' + parser_code + '\nENDOFFILE')
stdout.channel.recv_exit_status()

# Verify
stdin, stdout, stderr = ssh.exec_command('wc -l /opt/douyin-script/backend/app/services/parser_douyin.py')
print(f'Lines: {stdout.read().decode()}')

# Restart backend
print('Restarting backend...')
stdin, stdout, stderr = ssh.exec_command('kill -9 $(lsof -ti :8002) 2>/dev/null; sleep 2')
stdout.channel.recv_exit_status()
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 > /tmp/project.log 2>&1 &')
stdout.channel.recv_exit_status()

import time
time.sleep(3)

stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep 8002')
print(stdout.read().decode())

ssh.close()
print('✅ parser_douyin.py updated with 5-service rotation and backend restarted')
