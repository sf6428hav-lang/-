import httpx, re, json

# 1. Scan botvod.com
print("=== botvod.com ===")
r = httpx.get("https://www.botvod.com/", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=15)
html = r.text
forms = re.findall(r'<form[^>]*action=["\x27]([^"\x27]+)["\x27]', html)
fetches = re.findall(r'fetch\(["\x27]([^"\x27]+)["\x27]', html)
apis = re.findall(r'["\x27](/api/[^"\x27]+)["\x27]', html)
post_urls = re.findall(r'\.post\(["\x27]([^"\x27]+)["\x27]', html)
print(f"Forms: {forms}")
print(f"Fetches: {fetches}")
print(f"APIs: {apis}")
print(f"Post URLs: {post_urls}")
print(f"Page size: {len(html)} chars")

# 2. Scan snapany.com
print("\n=== snapany.com ===")
r = httpx.get("https://snapany.com/zh", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=15)
html = r.text
forms = re.findall(r'<form[^>]*action=["\x27]([^"\x27]+)["\x27]', html)
fetches = re.findall(r'fetch\(["\x27]([^"\x27]+)["\x27]', html)
apis = re.findall(r'["\x27](/api/[^"\x27]+)["\x27]', html)
post_urls = re.findall(r'\.post\(["\x27]([^"\x27]+)["\x27]', html)
print(f"Forms: {forms}")
print(f"Fetches: {fetches}")
print(f"APIs: {apis}")
print(f"Post URLs: {post_urls}")
print(f"Page size: {len(html)} chars")

# 3. Search GitHub
print("\n=== GitHub: douyin download API ===")
headers = {"Accept": "application/vnd.github.v3+json"}
r = httpx.get("https://api.github.com/search/repositories?q=douyin+download+api+free&sort=stars&order=desc&per_page=15", headers=headers, timeout=15)
data = r.json()
for repo in data.get("items", [])[:15]:
    stars = repo["stargazers_count"]
    name = repo["full_name"]
    desc = repo.get("description", "") or ""
    print(f"{stars:>6} stars | {name}")
    print(f"       {desc[:100]}")

# 4. Search for similar services
print("\n=== GitHub: video download service ===")
r = httpx.get("https://api.github.com/search/repositories?q=video+download+no+watermark+api&sort=stars&order=desc&per_page=10", headers=headers, timeout=15)
data = r.json()
for repo in data.get("items", [])[:10]:
    stars = repo["stargazers_count"]
    name = repo["full_name"]
    desc = repo.get("description", "") or ""
    print(f"{stars:>6} stars | {name}")
    print(f"       {desc[:100]}")
