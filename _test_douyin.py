import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Test: media-parser on douyin URL constructed from correct vid
print("=== Test media-parser with douyin URL ===")
stdin, stdout, stderr = ssh.exec_command('''
cd /opt/douyin-script/backend && source venv/bin/activate && python3 << "PYEOF"
import httpx, json, re
from urllib.parse import urlparse, parse_qs, unquote

# Step 1: Get vid from redirect URL
url = "https://novelquickapp.com/s/laBIj58ouLY/"
resp = httpx.get(url, follow_redirects=True, timeout=30,
    headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"})
parsed = urlparse(str(resp.url))
params = parse_qs(parsed.query)
zlink = unquote(params["zlink"][0])
if "%" in zlink:
    zlink = unquote(zlink)
vid_match = re.search(r'"vid"\\s*:\\s*"(\\d+)"', zlink)
vid = vid_match.group(1)
print(f"Extracted vid: {vid}")

# Step 2: Construct douyin URL
douyin_url = f"https://www.douyin.com/video/{vid}"
print(f"Douyin URL: {douyin_url}")

# Step 3: Use media-parser on douyin URL
resp = httpx.post("http://127.0.0.1:8051/api/parse", json={"text": douyin_url}, timeout=60)
data = resp.json()
print(f"succ: {data.get('succ')}")
print(f"title: {data.get('data', {}).get('title', 'N/A')}")
print(f"video_url: {data.get('data', {}).get('video_url', 'N/A')[:200]}")
print(f"retdesc: {data.get('retdesc', 'N/A')}")
PYEOF
''', timeout=60)
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()