import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# 直接测试：用最简单的prompt，看模型能不能"看到"视频内容
print("=== 直接测试API ===")
test_code = '''
import base64, tempfile, subprocess
from pathlib import Path
from openai import OpenAI

video = Path("/opt/douyin-script/backend/downloads/6ca0f698-a3e8-4485-9dff-569cf929a887.mp4")
client = OpenAI(
    api_key="gg-gcli-MJ37eKXis0slZoeiW379ej3wF1CGi8Z0QVjJRESkdzA",
    base_url="https://gcli.ggchan.dev/v1"
)

with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)
    # Extract audio
    audio_path = tmpdir / "audio.mp3"
    subprocess.run(["ffmpeg", "-y", "-i", str(video), "-vn", "-c:a", "libmp3lame", "-b:a", "32k", "-ac", "1", str(audio_path)], capture_output=True)
    audio_b64 = base64.b64encode(audio_path.read_bytes()).decode()
    
    # Extract 3 frames only
    frames_dir = tmpdir / "frames"
    frames_dir.mkdir()
    subprocess.run(["ffmpeg", "-y", "-i", str(video), "-vf", "fps=1/10,scale=640:-2", "-q:v", "10", str(frames_dir / "f_%04d.jpg")], capture_output=True)
    frames = sorted(frames_dir.glob("f_*.jpg"))
    
    print(f"Audio: {len(audio_path.read_bytes())/1024:.0f}KB, Frames: {len(frames)}")
    
    # Build request with ONLY 3 frames + simple prompt
    content = [
        {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "mp3"}}
    ]
    for f in frames:
        fb64 = base64.b64encode(f.read_bytes()).decode()
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{fb64}", "detail": "low"}})
    content.append({"type": "text", "text": "请描述这个视频：这是什么类型的视频？画面里有什么？人物在说什么？"})
    
    print(f"Content parts: {len(content)}, sending...")
    resp = client.chat.completions.create(
        model="gemini-3.1-pro-preview",
        messages=[{"role": "user", "content": content}]
    )
    print(f"Response ({len(resp.choices[0].message.content)} chars):")
    print(resp.choices[0].message.content[:2000])
'''

stdin, stdout, stderr = ssh.exec_command(f'cd /opt/douyin-script/backend && source venv/bin/activate && python3 -c \'{test_code}\'', timeout=120)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

ssh.close()