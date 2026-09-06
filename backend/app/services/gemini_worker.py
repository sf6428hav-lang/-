import os
import base64
from pathlib import Path
from openai import OpenAI
from ..config import settings
from ..prompt_template import MAHJONG_PROMPT


def generate_script(video_path: Path, custom_prompt: str = None) -> str:
    """Send video to Gemini via OpenAI-compatible API and get formatted script."""

    if not settings.gemini_api_key:
        raise ValueError("Gemini API Key not configured. Please set GEMINI_API_KEY in .env")

    client = OpenAI(
        api_key=settings.gemini_api_key,
        base_url=settings.gemini_api_base_url,
    )

    prompt = custom_prompt or MAHJONG_PROMPT

    # Read video file and encode as base64
    video_data = video_path.read_bytes()
    video_b64 = base64.b64encode(video_data).decode('utf-8')

    # Determine MIME type
    suffix = video_path.suffix.lower()
    mime_map = {
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo',
        '.webm': 'video/webm',
        '.mkv': 'video/x-matroska',
    }
    mime_type = mime_map.get(suffix, 'video/mp4')

    response = client.chat.completions.create(
        model=settings.gemini_model or "gemini-1.5-pro",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "video",
                        "video": f"data:{mime_type};base64,{video_b64}"
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content
