import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Write test script
code = '''
import httpx, re, json, subprocess, os
from urllib.parse import urlparse, parse_qs, unquote

url = "https://novelquickapp.com/s/laBIj58ouLY/"

# 1. Follow redirect
resp = httpx.get(url, follow_redirects=True, timeout=30,
    headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"})
redirect_url = str(resp.url)
print(f"Redirect URL: {redirect_url[:200]}")

# 2. Extract vid from zlink
parsed = urlparse(redirect_url)
params = parse_qs(parsed.query)
zlink = unquote(params["zlink"][0])
vid_match = re.search(r'"vid"\s*:\s*"(\d+)"', zlink)
vid = vid_match.group(1) if vid_match else None
print(f"Extracted vid: {vid}")

# 3. Construct douyin URL
douyin_url = f"https://www.douyin.com/video/{vid}"
print(f"Douyin URL: {douyin_url}")

# 4. Download with yt-dlp
os.chdir("/opt/douyin-script/backend/downloads")
r = subprocess.run(["yt-dlp", "--dump-json", "--no-download", douyin_url],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    info = json.loads(r.stdout)
    print(f"Title: {info.get('title', 'N/A')}")
    print(f"Description: {info.get('description', 'N/A')[:200]}")
    print(f"ID: {info.get('id', 'N/A')}")
else:
    print(f"yt-dlp failed: {r.stderr[:500]}")
'''

stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/test_vid.py << "EOF"\n{code}\nEOF')
stdout.channel.recv_exit_status()

stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && python3 /tmp/test_vid.py', timeout=60)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

ssh.close()