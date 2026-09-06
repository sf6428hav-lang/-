import os
from pathlib import Path
from google import genai
from ..config import settings
from ..prompt_template import MAHJONG_PROMPT

async def generate_script(video_path: Path, custom_prompt: str = None) -> str:
    """Send video to Gemini 3.1 Pro and get formatted script."""
    
    if not settings.gemini_api_key:
        raise ValueError("Gemini API Key not configured. Please set GEMINI_API_KEY in .env")

    client = genai.Client(
        api_key=settings.gemini_api_key,
        http_options={"base_url": settings.gemini_api_base_url} if settings.gemini_api_base_url else None,
    )
    
    prompt = custom_prompt or MAHJONG_PROMPT
    
    file_size = video_path.stat().st_size
    
    # Use File API for uploading
    uploaded_file = client.files.upload(file=str(video_path))
    
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=[uploaded_file, prompt]
    )
    
    # Clean up uploaded file
    try:
        client.files.delete(name=uploaded_file.name)
    except Exception:
        pass
    
    return response.text
