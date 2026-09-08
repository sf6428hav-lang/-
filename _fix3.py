import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Write fixed parser
parser_code = '''import httpx, re, asyncio
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path
from ..config import settings
from .parser import ParseResult

async def parse_hongguo(url: str) -> ParseResult:
    """红果短剧：从zlink提取vid→构造抖音URL→用media-parser获取直链"""
    dest_dir = settings.downloads_dir

    # 1. Follow redirect
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        resp = await client.get(url, headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        })
        redirect_url = str(resp.url)

    # 2. Extract vid from zlink
    parsed = urlparse(redirect_url)
    params = parse_qs(parsed.query)
    vid = None
    if "zlink" in params:
        zlink = unquote(params["zlink"][0])
        if "%" in zlink:
            zlink = unquote(zlink)
        match = re.search(r'"vid"\\s*:\\s*"(\\d+)"', zlink)
        if match:
            vid = match.group(1)
    if not vid:
        raise ValueError("Could not extract vid from Hongguo redirect URL")

    # 3. Construct douyin URL, use media-parser to get video URL
    douyin_url = f"https://www.douyin.com/video/{vid}"
    print(f"Hongguo -> Douyin: {douyin_url}")

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{settings.media_parser_url}/api/parse", json={"text": douyin_url})
        resp.raise_for_status()
        data = resp.json()
        if not data.get("succ"):
            raise ValueError(f"media-parser failed: {data.get('retdesc', 'unknown')}")
        result = data.get("data", {})
        video_url = result.get("video_url", "")
        title = result.get("title", "") or "红果短剧"
        if not video_url:
            raise ValueError("media-parser returned no video URL")

    return ParseResult(
        platform="hongguo",
        video_url=video_url,
        title=title,
        metadata={"source_url": url, "video_id": vid, "douyin_url": douyin_url}
    )
'''

stdin, stdout, stderr = ssh.exec_command(f'cat > /opt/douyin-script/backend/app/services/parser_hongguo.py << "EOF"\n{parser_code}\nEOF')
stdout.channel.recv_exit_status()

# Restart
stdin, stdout, stderr = ssh.exec_command('kill -9 $(lsof -ti :8002) 2>/dev/null; sleep 2')
stdout.channel.recv_exit_status()
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 > /tmp/project.log 2>&1 &')
stdout.channel.recv_exit_status()
time.sleep(3)
stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep 8002')
print("Port:", stdout.read().decode().strip())

# Test
print("\n=== Testing ===")
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -X POST http://localhost:8002/api/generate -H "Content-Type: application/json" -d \'{"links":["https://novelquickapp.com/s/laBIj58ouLY/"]}\'',
    timeout=180
)
print(stdout.read().decode('utf-8', errors='replace')[:2000])

print("\n=== Logs ===")
stdin, stdout, stderr = ssh.exec_command('tail -20 /tmp/project.log')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()