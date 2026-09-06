import httpx
import re
import json
from .parser import ParseResult

async def parse_hongguo(url: str) -> ParseResult:
    """Parse Hongguo (红果短剧) video URL"""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                      "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    }

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        try:
            resp = await client.get(url, headers=headers)
            html = resp.text
            final_url = str(resp.url)
        except Exception as e:
            raise ValueError(f"Failed to fetch Hongguo page: {e}")

    video_url = None
    title = ""

    # Look for video URLs in page content
    patterns = [
        r'playAddr[\'":\s]*[\'"](https?://[^\'"]+)[\'"]',
        r'play_url[\'":\s]*[\'"](https?://[^\'"]+)[\'"]',
        r'src[\'":\s]*[\'"]?(https?://[^\'"\s]+\.mp4[^\'"\s]*)',
        r'"url"[\'":\s]*[\'"](https?://[^\'"]+\.mp4[^\'"]*)[\'"]',
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            video_url = match.group(1)
            break

    # Try to extract title from page
    m = re.search(r"<title>([^<]+)</title>", html)
    if m:
        title = m.group(1)

    # Try to extract from JSON-LD or meta tags
    if not title:
        m = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', html)
        if m:
            title = m.group(1)

    if not video_url:
        raise ValueError(
            "Could not extract Hongguo video URL. "
            "The page structure may have changed."
        )

    return ParseResult(
        platform="hongguo",
        video_url=video_url,
        title=title or "Unknown Drama",
        metadata={"source_url": url}
    )
