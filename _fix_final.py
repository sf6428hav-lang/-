import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Write the fixed parser_hongguo.py directly to server
code = '''
import httpx, re, asyncio
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path
from ..config import settings
from .parser import ParseResult

async def parse_hongguo(url: str) -> ParseResult:
    """红果短剧：从重定向URL的zlink中提取vid，转抖音链接用yt-dlp下载"""
    dest_dir = settings.downloads_dir

    # 1. Follow redirect to get real URL
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        resp = await client.get(url, headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        })
        redirect_url = str(resp.url)

    # 2. Extract vid from zlink parameter
    parsed = urlparse(redirect_url)
    params = parse_qs(parsed.query)
    vid = None
    
    if "zlink" in params:
        zlink = unquote(params["zlink"][0])
        # Double decode if needed
        if "%" in zlink:
            zlink = unquote(zlink)
        match = re.search(r'"vid"\s*:\s*"(\d+)"', zlink)
        if match:
            vid = match.group(1)
    
    if not vid:
        raise ValueError("Could not extract vid from Hongguo redirect URL")

    # 3. Construct douyin URL and use yt-dlp
    douyin_url = f"https://www.douyin.com/video/{vid}"
    print(f"Hongguo -> Douyin: {douyin_url}")

    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-o", str(dest_dir / "%(id)s.%(ext)s"),
        "-f", "best[ext=mp4]/best",
        "--quiet", "--no-warnings",
        "--socket-timeout", "30",
        "--print", "after_move:filepath",
        douyin_url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(dest_dir)
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise ValueError(f"yt-dlp failed: {stderr.decode('utf-8', errors='replace')[:500]}")

    filepath = stdout.decode("utf-8").strip()
    if not filepath or not Path(filepath).exists():
        raise ValueError("yt-dlp did not produce a valid file")

    # 4. Get title
    title = ""
    info_proc = await asyncio.create_subprocess_exec(
        "yt-dlp", "--dump-json", "--no-download", douyin_url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    info_stdout, _ = await info_proc.communicate()
    if info_proc.returncode == 0:
        import json
        info = json.loads(info_stdout.decode("utf-8"))
        title = info.get("title", "") or info.get("description", "")[:100]

    return ParseResult(
        platform="hongguo",
        video_url="",
        title=title or "红果短剧",
        metadata={"source_url": url, "video_id": vid},
        local_path=filepath
    )
'''

stdin, stdout, stderr = ssh.exec_command(f'cat > /opt/douyin-script/backend/app/services/parser_hongguo.py << "EOF"\n{code}\nEOF')
stdout.channel.recv_exit_status()

print("=== Parser updated ===")

# Restart backend
stdin, stdout, stderr = ssh.exec_command('kill -9 $(lsof -ti :8002) 2>/dev/null; sleep 2')
stdout.channel.recv_exit_status()
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 > /tmp/project.log 2>&1 &')
stdout.channel.recv_exit_status()
time.sleep(3)

print("=== Backend restarted ===")
stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep 8002')
print(stdout.read().decode())

# Test end-to-end
print("\n=== Testing end-to-end ===")
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -X POST http://localhost:8002/api/generate '
    '-H "Content-Type: application/json" '
    '-d \'{"links":["https://novelquickapp.com/s/laBIj58ouLY/"]}\'',
    timeout=180
)
result = stdout.read().decode('utf-8', errors='replace')
print(result[:3000])

print("\n=== Backend logs ===")
stdin, stdout, stderr = ssh.exec_command('tail -30 /tmp/project.log')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()