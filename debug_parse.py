import httpx, json, subprocess, os

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
