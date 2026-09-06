import httpx
import re
from .parser import ParseResult

async def parse_douyin(url: str) -> ParseResult:
    """Parse Douyin short drama link.
    
    This is a placeholder implementation. In production, this would use
    yzfly/douyin-mcp-server or Douyin_TikTok_Download_API.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                      "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Referer": "https://www.douyin.com/",
    }

    # First, resolve short link to full URL
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        try:
            resp = await client.get(url, headers=headers)
            final_url = str(resp.url)
        except Exception as e:
            raise ValueError(f"Failed to resolve Douyin URL: {e}")

    # Try to extract video info from the page
    html = resp.text if hasattr(resp, 'text') else ""
    
    video_url = None
    title = ""

    # Look for video URLs in page content
    patterns = [
        r'playAddr[\'":\s]*[\'"](https?://[^\'"]+)[\'"]',
        r'play_url[\'":\s]*[\'"](https?://[^\'"]+)[\'"]',
        r'src[\'":\s]*[\'"]?(https?://[^\'"\s]+\.mp4[^\'"\s]*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            video_url = match.group(1)
            break

    # Extract title
    m = re.search(r"<title>([^<]+)</title>", html)
    if m:
        title = m.group(1)

    if not video_url:
        raise ValueError(
            "Could not extract Douyin video URL. "
            "Please ensure douyin-mcp-server or Douyin_TikTok_Download_API is configured."
        )

    return ParseResult(
        platform="douyin",
        video_url=video_url,
        title=title or "Unknown Drama",
        metadata={"source_url": url}
    )
