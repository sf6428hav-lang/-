import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Test: construct douyin URL from vid, use media-parser on it
print("=== Testing media-parser with douyin URL ===")
stdin, stdout, stderr = ssh.exec_command('''
cd /opt/douyin-script/backend && source venv/bin/activate && python3 -c "
import httpx, json, re
from urllib.parse import urlparse, parse_qs, unquote

# Get redirect URL
url = 'https://novelquickapp.com/s/laBIj58ouLY/'
resp = httpx.get(url, follow_redirects=True, timeout=30,
    headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)'})

# Extract vid from zlink
parsed = urlparse(str(resp.url))
params = parse_qs(parsed.query)
zlink = unquote(params['zlink'][0])
if '%' in zlink:
    zlink = unquote(zlink)
vid_match = re.search(r'\"vid\"\s*:\s*\"(\d+)\"', zlink)
vid = vid_match.group(1)
print(f'vid: {vid}')

# Construct douyin URL
douyin_url = f'https://www.douyin.com/video/{vid}'
print(f'Douyin URL: {douyin_url}')

# Use media-parser on douyin URL
resp = httpx.post('http://127.0.0.1:8051/api/parse', json={'text': douyin_url}, timeout=60)
data = resp.json()
print(f'Title: {data[\"data\"].get(\"title\", \"N/A\")}')
print(f'Video URL: {data[\"data\"].get(\"video_url\", \"N/A\")[:150]}')
print(f'Success: {data.get(\"succ\")}')
"
''', timeout=60)
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()