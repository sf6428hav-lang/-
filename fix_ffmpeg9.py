import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Write the complete new file
new_content = '''import base64
import tempfile
import subprocess
from pathlib import Path
from openai import OpenAI
from ..config import settings
from ..prompt_template import MAHJONG_PROMPT

FFMPEG = "/usr/bin/ffmpeg"


def generate_script(video_path: Path, custom_prompt: str = None) -> str:
    """Extract audio (MP3) + frames (2fps, q:v 20) from video, send to Gemini."""
    if not settings.gemini_api_key:
        raise ValueError("Gemini API Key not configured")

    client = OpenAI(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_api_base_url
    )

    prompt = custom_prompt or MAHJONG_PROMPT

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 1. Extract audio as MP3
        audio_path = tmpdir / "audio.mp3"
        subprocess.run([
            FFMPEG, "-y", "-i", str(video_path),
            "-vn", "-c:a", "libmp3lame", "-b:a", "32k",
            str(audio_path)
        ], check=True, capture_output=True)
        
        # 2. Extract frames at 2fps with q:v 20
        frames_dir = tmpdir / "frames"
        frames_dir.mkdir()
        subprocess.run([
            FFMPEG, "-y", "-i", str(video_path),
            "-vf", "fps=2",
            "-q:v", "20",
            str(frames_dir / "frame_%04d.jpg")
        ], check=True, capture_output=True)
        
        frames = sorted(frames_dir.glob("frame_*.jpg"))
        print(f"Extracted {len(frames)} frames")
        
        # 3. Build multipart content
        content = []
        
        # Add audio
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        content.append({
            "type": "input_audio",
            "input_audio": {
                "data": audio_base64,
                "format": "mp3"
            }
        })
        
        # Add frames
        for frame_path in frames:
            with open(frame_path, 'rb') as f:
                frame_data = f.read()
            frame_base64 = base64.b64encode(frame_data).decode('utf-8')
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame_base64}"
                }
            })
        
        # Add prompt
        content.append({
            "type": "text",
            "text": prompt
        })
        
        print(f"Sending to Gemini: {len(frames)} frames + audio")
        
        # 4. Send to Gemini
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{
                "role": "user",
                "content": content
            }],
            temperature=0.7
        )
        
        return response.choices[0].message.content
'''

stdin, stdout, stderr = ssh.exec_command('cat > /opt/douyin-script/backend/app/services/gemini_worker.py << "PYEOF"\n' + new_content + '\nPYEOF')
stdout.channel.recv_exit_status()

# Verify
stdin, stdout, stderr = ssh.exec_command("sed -n '9p' /opt/douyin-script/backend/app/services/gemini_worker.py")
new_line9 = stdout.read().decode('utf-8')
print(f'New Line 9: {new_line9}')

ssh.close()
