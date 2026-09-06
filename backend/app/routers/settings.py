from fastapi import APIRouter
from ..config import settings
from ..models import SettingsModel

router = APIRouter(prefix="/api", tags=["settings"])


@router.get("/settings")
async def get_settings():
    """Get current settings (API key masked)."""
    masked_key = ""
    if settings.gemini_api_key:
        if len(settings.gemini_api_key) > 8:
            masked_key = settings.gemini_api_key[:4] + "****" + settings.gemini_api_key[-4:]
        else:
            masked_key = "****"
    return {
        "api_base_url": settings.gemini_api_base_url,
        "api_key": masked_key,
        "prompt_template": "mahjong",
    }


@router.put("/settings")
async def update_settings(data: SettingsModel):
    """Update settings. For MVP, settings are stored in .env file."""
    env_path = settings.data_dir.parent / ".env"
    
    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
    
    # Update or add values
    keys_found = {}
    for i, line in enumerate(lines):
        if line.startswith("GEMINI_API_BASE_URL="):
            lines[i] = f"GEMINI_API_BASE_URL={data.api_base_url}"
            keys_found["base"] = True
        elif line.startswith("GEMINI_API_KEY="):
            # Only update if not masked
            if "****" not in data.api_key:
                lines[i] = f"GEMINI_API_KEY={data.api_key}"
            keys_found["key"] = True
    
    if "base" not in keys_found:
        lines.append(f"GEMINI_API_BASE_URL={data.api_base_url}")
    if "key" not in keys_found and "****" not in data.api_key:
        lines.append(f"GEMINI_API_KEY={data.api_key}")
    
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    
    # Update in-memory settings
    settings.gemini_api_base_url = data.api_base_url
    if "****" not in data.api_key:
        settings.gemini_api_key = data.api_key
    
    return {"message": "Settings saved"}
