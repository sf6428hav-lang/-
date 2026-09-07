import re
from typing import Optional

class ParseResult:
    def __init__(self, platform: str, video_url: str, title: str = "", metadata: dict = None, local_path: str = None):
        self.platform = platform
        self.video_url = video_url
        self.title = title
        self.metadata = metadata or {}
        self.local_path = local_path  # yt-dlp already downloaded the file

def detect_platform(url: str) -> str:
    if re.search(r"(douyin\.com|v\.douyin|tiktok\.com)", url, re.I):
        return "douyin"
    if re.search(r"(hongguo|novelquickapp|红果|changdunovel)", url, re.I):
        return "hongguo"
    return "unknown"

async def parse_link(url: str) -> Optional[ParseResult]:
    platform = detect_platform(url)
    if platform == "hongguo":
        from .parser_hongguo import parse_hongguo
        return await parse_hongguo(url)
    elif platform == "douyin":
        from .parser_douyin import parse_douyin
        return await parse_douyin(url)
    else:
        raise ValueError(f"Unsupported platform for URL: {url}")
