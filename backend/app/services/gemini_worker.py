import base64
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
        raise ValueError("Gemini API Key not configured. Please set GEMINI_API_KEY in .env")

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
            "-vn", "-c:a", "libmp3lame", "-b:a", "32k", "-ac", "1",
            str(audio_path)
        ], capture_output=True, check=True)
        
        audio_data = audio_path.read_bytes()
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        print(f"Audio: {len(audio_data) / 1024:.0f} KB")
        
        # 2. Extract frames at 2fps, 480p, JPEG quality 20
        frames_dir = tmpdir / "frames"
        frames_dir.mkdir()
        subprocess.run([
            FFMPEG, "-y", "-i", str(video_path),
            "-vf", "fps=2,scale=480:-2", "-q:v", "20",
            str(frames_dir / "frame_%04d.jpg")
        ], capture_output=True, check=True)
        
        frames = sorted(frames_dir.glob("frame_*.jpg"))
        total_frames = len(frames)
        total_frame_size = sum(f.stat().st_size for f in frames)
        print(f"Frames: {total_frames} images, {total_frame_size / 1024:.0f} KB total")
        
        # 3. Build content: audio + all frames + text prompt
        content_parts = [
            {
                "type": "input_audio",
                "input_audio": {
                    "data": audio_b64,
                    "format": "mp3"
                }
            }
        ]
        
        for frame_path in frames:
            frame_data = frame_path.read_bytes()
            frame_b64 = base64.b64encode(frame_data).decode('utf-8')
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame_b64}",
                    "detail": "low"
                }
            })
        
        content_parts.append({
            "type": "text",
            "text": prompt
        })
        
        total_size = len(audio_data) + total_frame_size
        print(f"Total payload: {total_size / 1024 / 1024:.2f} MB (base64: ~{total_size * 1.37 / 1024 / 1024:.2f} MB)")
        
        # 4. Send to Gemini
        response = client.chat.completions.create(
            model=settings.gemini_model or "gemini-1.5-pro",
            messages=[{
                "role": "user",
                "content": content_parts
            }]
        )
        
        return response.choices[0].message.content

