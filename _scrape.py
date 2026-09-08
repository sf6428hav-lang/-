import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Scrape Hongguo page directly to find the correct video URL
print("=== Scraping Hongguo page directly ===")
stdin, stdout, stderr = ssh.exec_command('''
cd /opt/douyin-script/backend && source venv/bin/activate && python3 << "PYEOF"
import httpx, re, json
from urllib.parse import unquote

url = "https://novelquickapp.com/s/laBIj58ouLY/"

# Follow redirect
resp = httpx.get(url, follow_redirects=True, timeout=30,
    headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"})
html = resp.text
print(f"Page size: {len(html)} chars")
print(f"Final URL: {resp.url}")

# Look for video URLs in various formats
print("\n--- Looking for video URLs ---")
# Search for mp4 URLs
mp4_urls = re.findall(r'https?://[^"\\s]+\\.mp4[^"\\s]*', html)
print(f"mp4 URLs found: {len(mp4_urls)}")
for u in mp4_urls[:3]:
    print(f"  {u[:150]}")

# Search for video URLs in JSON data
print("\n--- Looking for JSON data blocks ---")
for pattern_name, pattern in [
    ("__NEXT_DATA__", r'<script id="__NEXT_DATA__"[^>]*>([^<]+)</script>'),
    ("__NUXT__", r'window\.__NUXT__\s*=\s*({.+?});'),
    ("RENDER_DATA", r'<script[^>]*id="RENDER_DATA"[^>]*>([^<]+)</script>'),
]:
    m = re.search(pattern, html, re.DOTALL)
    if m:
        data_str = m.group(1)
        print(f"Found {pattern_name}: {len(data_str)} chars")
        # Try to decode if URL-encoded
        if "%" in data_str[:50]:
            try:
                data_str = unquote(data_str)
            except:
                pass
        # Look for video URLs in the data
        urls = re.findall(r'https?://[^"\\]+\.mp4[^"\\]*', data_str)
        if urls:
            print(f"  Found {len(urls)} mp4 URLs in data")
            for u in urls[:3]:
                print(f"  {u[:150]}")

# Search for qznovel.com / bytecdn URLs
print("\n--- Looking for qznovel/bytecdn URLs ---")
cdn_urls = re.findall(r'https?://[^"\\s]*(?:qznovel|bytevclod|bytecdn|snssdk)[^"\\s]*', html)
print(f"CDN URLs found: {len(cdn_urls)}")
for u in cdn_urls[:5]:
    print(f"  {u[:150]}")

# The page might have a different structure - look for data in script tags
print("\n--- Looking for data in script tags ---")
scripts = re.findall(r'<script[^>]*>([^<]+)</script>', html, re.DOTALL)
for i, script in enumerate(scripts):
    if len(script) > 1000 and ("video" in script.lower() or "play" in script.lower()):
        urls = re.findall(r'https?://[^"\\]+\.mp4[^"\\]*', script)
        if urls:
            print(f"Script {i} ({len(script)} chars): {len(urls)} mp4 URLs")
            for u in urls[:3]:
                print(f"    {u[:150]}")

PYEOF
''', timeout=60)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

ssh.close()