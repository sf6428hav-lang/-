import httpx
from pathlib import Path
from ..config import settings

async def download_video(video_url: str, filename: str) -> Path:
    """Download video file to temporary storage."""
    dest = settings.downloads_dir / filename
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                      "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    }
    async with httpx.AsyncClient(follow_redirects=True, timeout=300) as client:
        async with client.stream("GET", video_url, headers=headers) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                async for chunk in resp.aiter_bytes(chunk_size=65536):
                    f.write(chunk)
    print(f"Downloaded: {dest.name} ({dest.stat().st_size / 1024 / 1024:.2f} MB)")
    return dest

def cleanup_video(path: Path):
    try:
        if path and path.exists():
            path.unlink()
    except:
        pass
