import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Scrape Hongguo page directly
code = '''
import httpx, re, json
from urllib.parse import unquote

url = "https://novelquickapp.com/s/laBIj58ouLY/"
resp = httpx.get(url, follow_redirects=True, timeout=30,
    headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"})
html = resp.text
print(f"Page size: {len(html)} chars")

# Look for video URLs
mp4_urls = re.findall(r"https?://[^\\\"\\s]+\.mp4[^\\\"\\s]*", html)
print(f"mp4 URLs: {len(mp4_urls)}")
for u in mp4_urls[:3]:
    print(f"  {u[:150]}")

# Look for qznovel/byte URLs
cdn_urls = re.findall(r"https?://[^\\\"\\s]*(?:qznovel|bytevclod|bytecdn|snssdk)[^\\\"\\s]*", html)
print(f"CDN URLs: {len(cdn_urls)}")
for u in cdn_urls[:5]:
    print(f"  {u[:150]}")

# Look for JSON data in script tags
for pattern_name, pattern in [
    ("__NEXT_DATA__", r"<script id=\\"__NEXT_DATA__\\"[^>]*>([^<]+)</script>"),
    ("RENDER_DATA", r"<script[^>]*id=\\"RENDER_DATA\\"[^>]*>([^<]+)</script>"),
]:
    m = re.search(pattern, html, re.DOTALL)
    if m:
        data_str = m.group(1)
        print(f"Found {pattern_name}: {len(data_str)} chars")
        if "%" in data_str[:50]:
            data_str = unquote(data_str)
        urls = re.findall(r"https?://[^\\\"\\]+\.mp4[^\\\"\\]*", data_str)
        if urls:
            print(f"  mp4 URLs: {len(urls)}")
            for u in urls[:3]:
                print(f"    {u[:150]}")
'''

stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/scrape.py << "EOF"\n{code}\nEOF')
stdout.channel.recv_exit_status()
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && python3 /tmp/scrape.py', timeout=60)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

ssh.close()