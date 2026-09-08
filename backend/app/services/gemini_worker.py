import base64
import tempfile
import subprocess
from pathlib import Path
from openai import OpenAI
from ..config import settings
from ..prompt_template import MAHJONG_PROMPT

FFMPEG = "/usr/bin/ffmpeg"
MAX_FRAMES = 80

def generate_script(video_path: Path, custom_prompt: str = None) -> str:
    if not settings.gemini_api_key:
        raise ValueError("Gemini API Key not configured")

    client = OpenAI(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_api_base_url
    )

    prompt = custom_prompt or MAHJONG_PROMPT
    model = settings.gemini_model or "gemini-1.5-pro"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        probe = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)
        ], capture_output=True, text=True)
        duration = float(probe.stdout.strip() or 30)

        fps = max(1, round(MAX_FRAMES / duration * 2) / 2)
        if fps > 2:
            fps = 2
        print(f"Video: {duration:.0f}s, fps: {fps}")

        audio_path = tmpdir / "audio.mp3"
        subprocess.run([FFMPEG, "-y", "-i", str(video_path), "-vn", "-c:a", "libmp3lame", "-b:a", "32k", "-ac", "1", str(audio_path)], check=True, capture_output=True)
        audio_data = audio_path.read_bytes()
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")
        print(f"Audio: {len(audio_data) / 1024:.0f} KB")

        frames_dir = tmpdir / "frames"
        frames_dir.mkdir()
        subprocess.run([FFMPEG, "-y", "-i", str(video_path), "-vf", f"fps={fps},scale=480:-2", "-q:v", "25", str(frames_dir / "frame_%04d.jpg")], check=True, capture_output=True)

        frames = sorted(frames_dir.glob("frame_*.jpg"))
        total_frame_size = sum(f.stat().st_size for f in frames)
        print(f"Frames: {len(frames)} images, {total_frame_size / 1024:.0f} KB total")

        content = [{"type": "input_audio", "input_audio": {"data": audio_b64, "format": "mp3"}}]
        for frame_path in frames:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(frame_path.read_bytes()).decode()}", "detail": "low"}})
        content.append({"type": "text", "text": prompt})

        total_size = len(audio_data) + total_frame_size
        print(f"Total: {total_size / 1024 / 1024:.2f} MB (base64: ~{total_size * 1.37 / 1024 / 1024:.2f} MB)")

        response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": content}])
        return response.choices[0].message.content
