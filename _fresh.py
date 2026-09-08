import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# 1. Fresh parse + immediate download + immediate test
print("=== Fresh parse + immediate download + verify ===")
stdin, stdout, stderr = ssh.exec_command('''
cd /opt/douyin-script/backend && source venv/bin/activate && python3 << 'PYEOF'
import httpx, tempfile, subprocess, base64, json
from pathlib import Path

# Step 1: Get fresh video URL
print("1. Parsing...")
resp = httpx.post("http://127.0.0.1:8051/api/parse", json={"text": "https://novelquickapp.com/s/laBIj58ouLY/"}, timeout=60)
data = resp.json()
video_url = data["data"]["video_url"]
title = data["data"]["title"]
vid = data["data"]["video_id"]
print(f"   Title: {title}")
print(f"   Video ID: {vid}")

# Step 2: Download immediately
print("2. Downloading...")
with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)
    video_path = tmpdir / "test.mp4"
    dl = httpx.get(video_url, follow_redirects=True, timeout=60)
    video_path.write_bytes(dl.content)
    print(f"   Size: {video_path.stat().st_size / 1024 / 1024:.1f} MB")

    # Step 3: Extract audio + frames
    print("3. Extracting audio + frames...")
    subprocess.run(["ffmpeg", "-y", "-i", str(video_path), "-vn", "-c:a", "libmp3lame", "-b:a", "32k", "-ac", "1", str(tmpdir / "audio.mp3")], capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-i", str(video_path), "-vf", "fps=2,scale=640:-2", "-q:v", "20", str(tmpdir / "f_%04d.jpg")], capture_output=True)
    frames = sorted(tmpdir.glob("f_*.jpg"))
    print(f"   Audio: {(tmpdir/'audio.mp3').stat().st_size/1024:.0f}KB, Frames: {len(frames)}")

    # Step 4: Send to Gemini
    print("4. Sending to Gemini...")
    from openai import OpenAI
    client = OpenAI(api_key="gg-gcli-MJ37eKXis0slZoeiW379ej3wF1CGi8Z0QVjJRESkdzA", base_url="https://gcli.ggchan.dev/v1")
    audio_b64 = base64.b64encode((tmpdir/"audio.mp3").read_bytes()).decode()
    
    content = [{"type": "input_audio", "input_audio": {"data": audio_b64, "format": "mp3"}}]
    for f in frames:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(f.read_bytes()).decode()}", "detail": "low"}})
    content.append({"type": "text", "text": "请用一句话描述这个视频的故事内容，并说出主角的名字。"})
    
    resp = client.chat.completions.create(model="gemini-3.1-pro-preview", messages=[{"role": "user", "content": content}])
    result = resp.choices[0].message.content
    print(f"5. AI Response ({len(result)} chars):")
    print(result[:500])
PYEOF
''', timeout=180)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

ssh.close()