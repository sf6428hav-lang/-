import httpx
from ..config import settings
from .parser import ParseResult

async def parse_hongguo(url: str) -> ParseResult:
    """Use media-parser for Hongguo (red fruit) video links."""
    api_url = f"{settings.media_parser_url}/api/parse"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(api_url, json={"text": url})
            resp.raise_for_status()
            data = resp.json()
            
            if not data.get("succ"):
                raise ValueError(f"Media-parser error: {data.get('retdesc', 'Unknown error')}")
            
            result = data.get("data", {})
            video_url = result.get("video_url", "")
            title = result.get("title", "")
            
            if not video_url:
                raise ValueError("Media-parser did not return a video URL")
            
            metadata = {
                "author": result.get("author", {}),
                "video_id": result.get("video_id", ""),
                "cover_url": result.get("cover_url", ""),
                "audio_url": result.get("audio_url", ""),
                "image_list": result.get("image_list", [])
            }
            
            return ParseResult(
                platform="hongguo",
                video_url=video_url,
                title=title or "红果短剧",
                metadata=metadata
            )
            
        except httpx.HTTPError as e:
            raise ValueError(f"Media-parser request failed: {e}")
        except Exception as e:
            raise ValueError(f"Hongguo video parse failed: {e}")
