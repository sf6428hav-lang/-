import asyncio
import re
from pathlib import Path
from ..config import settings
from .parser import ParseResult

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

SERVICES = [
    { 'name': 'tiksave.io',          'url': 'https://tiksave.io/api/ajaxSearch',        'data_fn': lambda u: {'q': u, 'lang': 'en'}, },
    { 'name': 'tikdownloader.io',    'url': 'https://tikdownloader.io/api/ajaxSearch',   'data_fn': lambda u: {'q': u, 'lang': 'en'}, },
    { 'name': 'tikdownloader.app',   'url': 'https://tikdownloader.app/api/ajaxSearch',  'data_fn': lambda u: {'q': u, 'lang': 'en'}, },
    { 'name': 'savetik.co',          'url': 'https://savetik.co/api/ajaxSearch',         'data_fn': lambda u: {'q': u, 'lang': 'en'}, },
    { 'name': 'botvod.com',          'url': 'https://www.botvod.com/api/info',           'data_fn': lambda u: {'url': u}, 'use_json': True, },
]

def _extract_video_url(html_text):
    all_urls = re.findall(r"https?://[^\"'<>\s&]+", html_text.replace("&amp;", "&"))
    for u in all_urls:
        if any(x in u for x in ("zjcdn", "douyinvod", "bytedance", "byteicdn")):
            return u
    return None

async def parse_douyin(url: str) -> ParseResult:
    try:
        from curl_cffi import requests as cffi_requests
        USE_CURL = True
    except ImportError:
        import httpx
        USE_CURL = False

    for svc in SERVICES:
        try:
            if USE_CURL:
                session = cffi_requests.Session()
                headers = {"User-Agent": UA, "Referer": svc["url"].rsplit("/", 1)[0] + "/"}
                if svc.get("use_json"):
                    resp = session.post(svc["url"], json=svc["data_fn"](url), headers=headers, impersonate="chrome120", timeout=20)
                else:
                    resp = session.post(svc["url"], data=svc["data_fn"](url), headers=headers, impersonate="chrome120", timeout=20)
                if resp.status_code != 200:
                    print(f"[{svc['name']}] HTTP {resp.status_code}")
                    continue
                data = resp.json()
                video_url = data.get("url") if svc["name"] == "botvod.com" else _extract_video_url(data.get("data", ""))
            else:
                import httpx
                async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                    if svc.get("use_json"):
                        resp = await client.post(svc["url"], json=svc["data_fn"](url), headers={"User-Agent": UA})
                    else:
                        resp = await client.post(svc["url"], data=svc["data_fn"](url), headers={"User-Agent": UA})
                    if resp.status_code != 200:
                        continue
                    data = resp.json()
                    video_url = data.get("url") if svc["name"] == "botvod.com" else _extract_video_url(data.get("data", ""))
            
            if video_url:
                print(f"[{svc['name']}] Success")
                return ParseResult(platform="douyin", video_url=video_url, title="", metadata={"service": svc["name"]})
            print(f"[{svc['name']}] No video URL")
        except Exception as e:
            print(f"[{svc['name']}] Error: {str(e)[:80]}")
    
    raise ValueError("所有抖音解析服务均不可用")
