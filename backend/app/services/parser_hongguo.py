import httpx
import re
import json
from .parser import ParseResult

async def parse_hongguo(url: str) -> ParseResult:
    """Parse Hongguo (Red Fruit) short drama sharing link to get MP4 direct URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                      "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        html = resp.text

    # Try to extract video URL from page data
    video_url = None
    title = ""

    # Pattern 1: Look for play_url or videoUrl in script tags
    patterns = [
        r"play_url['":\s]+(['"])(https?://[^'"]+\.mp4[^'"]*)\1",
        r"videoUrl['":\s]+(['"])(https?://[^'"]+\.mp4[^'"]*)\1",
        r"video_url['":\s]+(['"])(https?://[^'"]+\.mp4[^'"]*)\1",
        r"src['":\s]*['"]?(https?://[^'"\s]+\.mp4[^'"\s]*)",
    ]

    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            video_url = match.group(2) if match.lastindex >= 2 else match.group(1)
            video_url = video_url.replace("\\u0026", "&").replace("\/", "/")
            break

    # Pattern 2: Look for JSON data blocks
    if not video_url:
        json_patterns = [
            r"window\.__INITIAL_STATE__\s*=\s*({.*?});",
            r"window\.__NEXT_DATA__\s*=\s*({.*?});",
        ]
        for jp in json_patterns:
            match = re.search(jp, html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    video_url = _extract_url_from_json(data)
                    if video_url:
                        break
                except (json.JSONDecodeError, TypeError):
                    continue

    # Extract title
    title_patterns = [
        r"<title>([^<]+)</title>",
        r"title['":\s]+(['"])([^'"]+)\1",
    ]
    for tp in title_patterns:
        m = re.search(tp, html)
        if m:
            title = m.group(m.lastindex)
            break

    if not video_url:
        raise ValueError("Could not extract video URL from Hongguo page")

    return ParseResult(
        platform="hongguo",
        video_url=video_url,
        title=title or "Unknown Drama",
        metadata={"source_url": url}
    )


def _extract_url_from_json(data, depth=0) -> str | None:
    if depth > 10:
        return None
    if isinstance(data, dict):
        for key in ["play_url", "videoUrl", "video_url", "url", "src", "mp4_url"]:
            if key in data and isinstance(data[key], str) and ".mp4" in data[key]:
                return data[key]
        for val in data.values():
            result = _extract_url_from_json(val, depth + 1)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = _extract_url_from_json(item, depth + 1)
            if result:
                return result
    return None
