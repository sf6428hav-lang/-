import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# 1. 解析新链接
print("=== 1. 解析新链接 ===")
stdin, stdout, stderr = ssh.exec_command('''
cd /opt/douyin-script/backend && source venv/bin/activate && python3 << "PYEOF"
import httpx, json, re
from urllib.parse import urlparse, parse_qs, unquote

url = "https://novelquickapp.com/s/wozKigocpho/"
resp = httpx.get(url, follow_redirects=True, timeout=30,
    headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"})
redirect = str(resp.url)
print(f"Redirect: {redirect[:200]}")

# Parse vid
parsed = urlparse(redirect)
params = parse_qs(parsed.query)
if "zlink" in params:
    zlink = unquote(params["zlink"][0])
    if "%" in zlink:
        zlink = unquote(zlink)
    m = re.search(r'"vid"\s*:\s*"(\d+)"', zlink)
    if m:
        print(f"vid: {m.group(1)}")

# media-parser
resp = httpx.post("http://127.0.0.1:8051/api/parse", json={"text": url}, timeout=60)
data = resp.json()
print(f"title: {data['data'].get('title')}")
print(f"video_id: {data['data'].get('video_id')}")
print(f"video_url: {data['data'].get('video_url', '')[:150]}")
PYEOF
''', timeout=60)
print(stdout.read().decode('utf-8', errors='replace'))

# 2. 下载验证
print("\n=== 2. 下载验证 ===")
stdin, stdout, stderr = ssh.exec_command('''
cd /opt/douyin-script/backend && source venv/bin/activate && python3 << "PYEOF"
import httpx, tempfile, subprocess, base64
from pathlib import Path

resp = httpx.post("http://127.0.0.1:8051/api/parse", json={"text": "https://novelquickapp.com/s/wozKigocpho/"}, timeout=60)
video_url = resp.json()["data"]["video_url"]
title = resp.json()["data"]["title"]

with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)
    vp = tmpdir / "test.mp4"
    dl = httpx.get(video_url, follow_redirects=True, timeout=60)
    vp.write_bytes(dl.content)
    
    subprocess.run(["ffmpeg", "-y", "-i", str(vp), "-vn", "-c:a", "libmp3lame", "-b:a", "32k", "-ac", "1", str(tmpdir/"a.mp3")], capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-i", str(vp), "-vf", "fps=2,scale=640:-2", "-q:v", "20", str(tmpdir/"f_%04d.jpg")], capture_output=True)
    frames = sorted(tmpdir.glob("f_*.jpg"))
    
    from openai import OpenAI
    client = OpenAI(api_key="gg-gcli-MJ37eKXis0slZoeiW379ej3wF1CGi8Z0QVjJRESkdzA", base_url="https://gcli.ggchan.dev/v1")
    audio_b64 = base64.b64encode((tmpdir/"a.mp3").read_bytes()).decode()
    
    content = [{"type": "input_audio", "input_audio": {"data": audio_b64, "format": "mp3"}}]
    for f in frames:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(f.read_bytes()).decode()}", "detail": "low"}})
    content.append({"type": "text", "text": "这个视频里主角叫什么名字？故事讲的是什么？请用一句话概括。"})
    
    resp = client.chat.completions.create(model="gemini-3.1-pro-preview", messages=[{"role": "user", "content": content}])
    print(f"Title from parser: {title}")
    print(f"AI: {resp.choices[0].message.content[:300]}")
PYEOF
''', timeout=180)
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()