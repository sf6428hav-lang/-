import httpx, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# botvod.com - find JS files and API calls
print("=== botvod.com deep scan ===")
r = httpx.get("https://www.botvod.com/", headers={"User-Agent": UA}, timeout=15)
html = r.text
scripts = re.findall(r'<script[^>]*src=["\x27]([^"\x27]+)["\x27]', html)
print(f"Script files: {scripts}")
# Look for inline JS with API calls
inline = re.findall(r'<script[^>]*>(.+?)</script>', html, re.DOTALL)
for i, s in enumerate(inline):
    if "api" in s.lower() or "fetch" in s.lower() or "axios" in s.lower() or "post" in s.lower():
        print(f"\nInline script {i} ({len(s)} chars):")
        # Find API URLs
        api_calls = re.findall(r'["\x27](https?://[^"\x27]*(?:api|parse|download)[^"\x27]*)["\x27]', s)
        if api_calls:
            print(f"  API URLs: {api_calls}")
        post_calls = re.findall(r'\.(?:post|get)\s*\(\s*["\x27]([^"\x27]+)["\x27]', s)
        if post_calls:
            print(f"  HTTP calls: {post_calls}")

# Fetch each JS file
for src in scripts[:10]:
    if not src.startswith("http"):
        src = "https://www.botvod.com" + src
    try:
        jr = httpx.get(src, headers={"User-Agent": UA}, timeout=10)
        js = jr.text
        api_urls = re.findall(r'["\x27](https?://[^"\x27]*(?:api|parse|download|extract)[^"\x27]*)["\x27]', js)
        post_calls = re.findall(r'\.(?:post|get)\s*\(\s*["\x27]([^"\x27]+)["\x27]', js)
        if api_urls or post_calls:
            print(f"\n{src}:")
            if api_urls: print(f"  API URLs: {api_urls[:5]}")
            if post_calls: print(f"  HTTP calls: {post_calls[:5]}")
    except:
        pass
