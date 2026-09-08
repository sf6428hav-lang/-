import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# 1. 用 media-parser 获取视频 URL，然后直接下载验证
print("=== 1. media-parser 解析 ===")
stdin, stdout, stderr = ssh.exec_command('''
cd /opt/douyin-script/backend && source venv/bin/activate && python3 -c "
import httpx, json
resp = httpx.post('http://127.0.0.1:8051/api/parse', json={'text': 'https://novelquickapp.com/s/laBIj58ouLY/'}, timeout=60)
data = resp.json()
print('title:', data['data'].get('title'))
print('video_id:', data['data'].get('video_id'))
print('video_url:', data['data'].get('video_url')[:150])
"
''')
print(stdout.read().decode('utf-8', errors='replace'))

# 2. 下载并验证视频内容
print("\n=== 2. 下载验证 ===")
stdin, stdout, stderr = ssh.exec_command('''
cd /opt/douyin-script/backend && source venv/bin/activate && python3 -c "
import httpx, tempfile, subprocess, base64, json
from pathlib import Path

# Get video URL
resp = httpx.post('http://127.0.0.1:8051/api/parse', json={'text': 'https://novelquickapp.com/s/laBIj58ouLY/'}, timeout=60)
video_url = resp.json()['data']['video_url']

# Download
with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)
    video_path = tmpdir / 'test.mp4'
    dl = httpx.get(video_url, follow_redirects=True, timeout=60)
    video_path.write_bytes(dl.content)
    print(f'Downloaded: {video_path.stat().st_size / 1024 / 1024:.1f} MB')
    
    # Extract 3 frames and audio
    subprocess.run(['ffmpeg', '-y', '-i', str(video_path), '-vn', '-c:a', 'libmp3lame', '-b:a', '32k', '-ac', '1', str(tmpdir / 'audio.mp3')], capture_output=True)
    subprocess.run(['ffmpeg', '-y', '-i', str(video_path), '-vf', 'fps=1/10,scale=640:-2', '-q:v', '10', str(tmpdir / 'f_%04d.jpg')], capture_output=True)
    
    frames = sorted(tmpdir.glob('f_*.jpg'))
    print(f'Frames: {len(frames)}')
    
    # Send to Gemini
    from openai import OpenAI
    client = OpenAI(api_key='gg-gcli-MJ37eKXis0slZoeiW379ej3wF1CGi8Z0QVjJRESkdzA', base_url='https://gcli.ggchan.dev/v1')
    audio_b64 = base64.b64encode((tmpdir / 'audio.mp3').read_bytes()).decode()
    
    content = [{'type': 'input_audio', 'input_audio': {'data': audio_b64, 'format': 'mp3'}}]
    for f in frames:
        content.append({'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{base64.b64encode(f.read_bytes()).decode()}', 'detail': 'low'}})
    content.append({'type': 'text', 'text': '这个视频讲的是什么故事？角色名字是什么？请用一句话概括。'})
    
    resp = client.chat.completions.create(model='gemini-3.1-pro-preview', messages=[{'role': 'user', 'content': content}])
    print(f'AI: {resp.choices[0].message.content[:500]}')
"
''', timeout=120)
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()