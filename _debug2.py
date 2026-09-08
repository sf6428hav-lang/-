import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Write test script to server
code = """import httpx, json, subprocess, os

url = "https://novelquickapp.com/s/laBIj58ouLY/"
print("=== 1. Original URL ===")
print(url)

print("\n=== 2. Redirect ===")
resp = httpx.get(url, follow_redirects=True, timeout=30,
    headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"})
print(f"Final URL: {resp.url}")

print("\n=== 3. Media-parser result ===")
resp = httpx.post("http://127.0.0.1:8051/api/parse", json={"text": url}, timeout=60)
data = resp.json()
print(json.dumps(data, indent=2, ensure_ascii=False))

print("\n=== 4. yt-dlp test ===")
os.chdir("/opt/douyin-script/backend/downloads")
r = subprocess.run(["yt-dlp", "--dump-json", "--no-download", url],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    info = json.loads(r.stdout)
    print(f"Title: {info.get('title', 'N/A')}")
    print(f"ID: {info.get('id', 'N/A')}")
    print(f"Description: {info.get('description', 'N/A')[:200]}")
else:
    print(f"yt-dlp failed: {r.stderr[:500]}")
"""

stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/debug.py << "EOF"\n{code}\nEOF')
stdout.channel.recv_exit_status()

stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && python3 /tmp/debug.py', timeout=60)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

ssh.close()