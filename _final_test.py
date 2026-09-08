import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Restore simple parser
parser_code = '''import httpx
from ..config import settings
from .parser import ParseResult

async def parse_hongguo(url: str) -> ParseResult:
    """Use media-parser for Hongguo (red fruit) video links."""
    api_url = f"{settings.media_parser_url}/api/parse"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
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
        
        return ParseResult(
            platform="hongguo",
            video_url=video_url,
            title=title or "红果短剧",
            metadata={"author": result.get("author", {}), "video_id": result.get("video_id", "")}
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
print("\n=== Test ===")
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -X POST http://localhost:8002/api/generate -H "Content-Type: application/json" -d \'{"links":["https://novelquickapp.com/s/laBIj58ouLY/"]}\'',
    timeout=180
)
result = stdout.read().decode('utf-8', errors='replace')
print(result[:3000])

# Get latest script
print("\n=== Latest script ===")
stdin, stdout, stderr = ssh.exec_command('ls -t /opt/douyin-script/backend/data/scripts/*.txt | head -1')
latest = stdout.read().decode().strip()
if latest:
    stdin, stdout, stderr = ssh.exec_command(f'cat "{latest}"')
    content = stdout.read()
    print(content.decode('utf-8', errors='replace')[:2000])

ssh.close()