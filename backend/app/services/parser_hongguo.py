import asyncio
import re
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path
import httpx
from ..config import settings
from .parser import ParseResult


def extract_video_id_from_url(url: str) -> str:
    """从红果重定向后的 URL 中提取 video_id"""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    # 直接参数
    if 'vid' in params:
        return params['vid'][0]
    if 'video_id' in params:
        return params['video_id'][0]
    
    # zlink 参数中的 video_id（双重编码）
    if 'zlink' in params:
        zlink = unquote(params['zlink'][0])
        if 'schemeParams' in zlink:
            # 再次解码
            scheme_part = unquote(unquote(zlink.split('schemeParams=')[-1].split('&')[0]))
            match = re.search(r'"vid"\s*:\s*"(\d+)"', scheme_part)
            if match:
                return match.group(1)
    
    # URL 中的 report_params (JSON 编码)
    if 'report_params' in params:
        report = unquote(params['report_params'][0])
        match = re.search(r'"vid"\s*:\s*"(\d+)"', report)
        if match:
            return match.group(1)
    
    return ""


async def parse_hongguo(url: str) -> ParseResult:
    """红果短剧：先提取 video_id，再转成抖音链接让 yt-dlp 下载"""
    dest_dir = settings.downloads_dir

    # 1. 先重定向获取真实 URL
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        try:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                              "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
            })
            redirect_url = str(resp.url)
            html = resp.text
        except Exception as e:
            raise ValueError(f"Failed to fetch Hongguo redirect URL: {e}")

    # 2. 提取 video_id
    video_id = extract_video_id_from_url(redirect_url)
    
    # 如果重定向没拿到，从 HTML 里找
    if not video_id:
        match = re.search(r'"vid"\s*:\s*"(\d+)"', html)
        if match:
            video_id = match.group(1)
    
    # 再试 report_params
    if not video_id:
        match = re.search(r'"video_id"\s*:\s*"(\d+)"', html)
        if match:
            video_id = match.group(1)

    if not video_id:
        raise ValueError("Could not extract video_id from Hongguo link")

    # 3. 构造抖音链接
    douyin_url = f"https://www.douyin.com/video/{video_id}"
    print(f"Hongguo -> Douyin: {douyin_url}")

    # 4. 用 yt-dlp 下载
    proc = await asyncio.create_subprocess_exec(
        'yt-dlp',
        '-o', str(dest_dir / '%(id)s.%(ext)s'),
        '-f', 'best[ext=mp4]/best',
        '--quiet', '--no-warnings',
        '--socket-timeout', '30',
        '--print', 'after_move:filepath',
        douyin_url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(dest_dir)
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise ValueError(f"yt-dlp failed for Hongguo->Douyin: {stderr.decode('utf-8', errors='replace')[:500]}")

    filepath = stdout.decode('utf-8').strip()
    if not filepath or not Path(filepath).exists():
        raise ValueError("yt-dlp did not produce a valid file path")

    # 5. 获取标题
    title = ""
    info_proc = await asyncio.create_subprocess_exec(
        'yt-dlp', '--dump-json', '--no-download', douyin_url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    info_stdout, _ = await info_proc.communicate()
    try:
        import json
        info = json.loads(info_stdout.decode('utf-8'))
        title = info.get('title', '') or info.get('description', '')[:100]
    except:
        pass

    return ParseResult(
        platform="hongguo",
        video_url="",
        title=title or "红果短剧",
        metadata={"source_url": url, "video_id": video_id},
        local_path=filepath
    )
