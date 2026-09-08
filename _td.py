import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Write test script to server
code = """
import subprocess, json, os, httpx, tempfile, base64
from pathlib import Path

url = "https://v.douyin.com/1CzGfFJVQD0/"
os.chdir("/opt/douyin-script/backend/downloads")

# 1. yt-dlp parse
print("=== yt-dlp parse ===")
r = subprocess.run(["yt-dlp", "--dump-json", "--no-download", url],
                   capture_output=True, text=True, timeout=30)
if r.returncode == 0:
    info = json.loads(r.stdout)
    print(f"Title: {info.get('title', 'N/A')}")
    print(f"Duration: {info.get('duration', 'N/A')}s")
else:
    print(f"FAILED: {r.stderr[:300]}")

# 2. Download and test with Gemini
print("\\n=== Download + Gemini test ===")
r = subprocess.run(["yt-dlp", "-o", "test_dl.%(ext)s", "-f", "best[ext=mp4]/best", "--quiet", url],
                   capture_output=True, text=True, timeout=60)
if r.returncode == 0:
    vp = Path("test_dl.mp4")
    print(f"Downloaded: {vp.stat().st_size / 1024 / 1024:.1f} MB")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        subprocess.run(["ffmpeg", "-y", "-i", str(vp), "-vn", "-c:a", "libmp3lame", "-b:a", "32k", "-ac", "1", str(tmpdir/"a.mp3")], capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-i", str(vp), "-vf", "fps=2,scale=640:-2", "-q:v", "20", str(tmpdir/"f_%04d.jpg")], capture_output=True)
        frames = sorted(tmpdir.glob("f_*.jpg"))

        from openai import OpenAI
        client = OpenAI(api_key="gg-gcli-MJ37eKXis0slZoeiW379ej3wF1CGi8Z0QVjJRESkdzA", base_url="https://gcli.ggchan.dev/v1")
        audio_b64 = base64.b64encode((tmpdir/"a.mp3").read_bytes()).decode()

        content = [{"type": "input_audio", "input_audio": {"data": audio_b64, "format": "mp3"}}]
        for f in frames:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(f.read_bytes()).decode()}", "detail": "low"}})
        content.append({"type": "text", "text": "这个视频的主角叫什么名字？故事讲的是什么？请用一句话概括。"})

        resp = client.chat.completions.create(model="gemini-3.1-pro-preview", messages=[{"role": "user", "content": content}])
        print(f"AI: {resp.choices[0].message.content[:300]}")
else:
    print(f"Download failed: {r.stderr[:300]}")
"""

stdin, stdout, stderr = ssh.exec_command(f'cat > /tmp/test_douyin.py << "EOF"\n{code}\nEOF')
stdout.channel.recv_exit_status()
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && python3 /tmp/test_douyin.py', timeout=120)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

ssh.close()