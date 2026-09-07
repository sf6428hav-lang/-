import asyncio
from pathlib import Path
from ..config import settings
from .parser import ParseResult

async def parse_hongguo(url: str) -> ParseResult:
    """Use yt-dlp to parse and download Hongguo video."""
    dest_dir = settings.downloads_dir

    proc = await asyncio.create_subprocess_exec(
        'yt-dlp',
        '-o', str(dest_dir / '%(id)s.%(ext)s'),
        '-f', 'best[ext=mp4]/best',
        '--quiet', '--no-warnings',
        '--socket-timeout', '30',
        '--print', 'after_move:filepath',
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(dest_dir)
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise ValueError(f"yt-dlp failed for Hongguo: {stderr.decode('utf-8', errors='replace')[:500]}")

    filepath = stdout.decode('utf-8').strip()
    if not filepath or not Path(filepath).exists():
        raise ValueError("yt-dlp did not produce a valid file path")

    # Get video info
    info_proc = await asyncio.create_subprocess_exec(
        'yt-dlp', '--dump-json', '--no-download', url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    info_stdout, _ = await info_proc.communicate()
    title = ""
    try:
        import json
        info = json.loads(info_stdout.decode('utf-8'))
        title = info.get('title', '') or info.get('description', '')[:100]
    except:
        pass

    return ParseResult(
        platform="hongguo",
        video_url="",
        title=title or "Hongguo Video",
        metadata={"source_url": url},
        local_path=filepath
    )
