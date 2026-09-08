import base64
import tempfile
import subprocess
from pathlib import Path
from openai import OpenAI
from ..config import settings
from ..prompt_template import MAHJONG_PROMPT

FFMPEG = "/usr/bin/ffmpeg"
BATCH_SIZE = 100  # 每批100帧
MIN_SIZE = 512    # 最小边长512像素


def generate_script(video_path: Path, custom_prompt: str = None) -> str:
    if not settings.gemini_api_key:
        raise ValueError("Gemini API Key not configured")

    client = OpenAI(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_api_base_url
    )
    model = settings.gemini_model or "gemini-1.5-pro"
    prompt = custom_prompt or MAHJONG_PROMPT

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 1. 提取音频
        audio_path = tmpdir / "audio.mp3"
        subprocess.run([
            FFMPEG, "-y", "-i", str(video_path),
            "-vn", "-c:a", "libmp3lame", "-b:a", "32k", "-ac", "1",
            str(audio_path)
        ], check=True, capture_output=True)
        audio_data = audio_path.read_bytes()
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")
        print(f"Audio: {len(audio_data) / 1024:.0f} KB")

        # 2. 提取帧：2fps, 512px最小边长
        frames_dir = tmpdir / "frames"
        frames_dir.mkdir()
        subprocess.run([
            FFMPEG, "-y", "-i", str(video_path),
            "-vf", f"fps=2,scale='min(512,iw)':-2", "-q:v", "20",
            str(frames_dir / "frame_%04d.jpg")
        ], check=True, capture_output=True)
        frames = sorted(frames_dir.glob("frame_*.jpg"))
        print(f"Frames: {len(frames)} images")

        # 3. 分批处理
        all_text = ""
        batch_count = (len(frames) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"Processing in {batch_count} batches")

        for batch_idx in range(batch_count):
            start = batch_idx * BATCH_SIZE
            end = min(start + BATCH_SIZE, len(frames))
            batch_frames = frames[start:end]
            batch_size = sum(f.stat().st_size for f in batch_frames)

            # 构建请求
            content = [{"type": "input_audio", "input_audio": {"data": audio_b64, "format": "mp3"}}]
            for f in batch_frames:
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(f.read_bytes()).decode()}", "detail": "low"}})

            # 第一段：正常请求
            if batch_idx == 0:
                content.append({"type": "text", "text": prompt})
            else:
                # 后续段：携带前文context
                context = f"""以下是你之前已经生成的前半部分剧本（第1-{batch_idx}段）：

{all_text}

请务必保持人物姓名、性格和剧情的连贯性，严格根据新画面接续往下写。不要重复之前已经写过的内容，直接从上一段结束的地方继续。"""
                content.append({"type": "text", "text": context})

            total = len(audio_data) + batch_size
            print(f"Batch {batch_idx+1}/{batch_count}: {len(batch_frames)} frames, {total / 1024 / 1024:.2f} MB (base64 ~{total * 1.37 / 1024 / 1024:.2f} MB)")

            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": content}]
            )
            part = resp.choices[0].message.content
            print(f"Batch {batch_idx+1} result: {len(part)} chars")

            all_text += part + "\n\n"

        return all_text.strip()
