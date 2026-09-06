from fastapi import APIRouter, Query
from openai import OpenAI
from ..config import settings
from ..models import SettingsModel

router = APIRouter(prefix="/api", tags=["settings"])


def normalize_base_url(url: str) -> str:
    url = url.rstrip('/')
    if not url.endswith('/v1'):
        url = url + '/v1'
    return url


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
        "model_name": settings.gemini_model,
        "prompt_template": "mahjong",
    }


@router.get("/models")
async def list_models(api_base_url: str = Query(default=""), api_key: str = Query(default="")):
    """Fetch available models from the API provider."""
    base_url = api_base_url or settings.gemini_api_base_url
    key = api_key or settings.gemini_api_key
    if not key or "****" in key:
        key = settings.gemini_api_key
    if not key:
        return {"models": [], "error": "请先配置 API Key"}

    try:
        client = OpenAI(
            api_key=key,
            base_url=normalize_base_url(base_url),
        )
        models = client.models.list()
        model_ids = [m.id for m in models.data]
        model_ids.sort()
        return {"models": model_ids}
    except Exception as e:
        return {"models": [], "error": str(e)}


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
            if "****" not in data.api_key:
                lines[i] = f"GEMINI_API_KEY={data.api_key}"
            keys_found["key"] = True
        elif line.startswith("GEMINI_MODEL="):
            lines[i] = f"GEMINI_MODEL={data.model_name}"
            keys_found["model"] = True

    if "base" not in keys_found:
        lines.append(f"GEMINI_API_BASE_URL={data.api_base_url}")
    if "key" not in keys_found and "****" not in data.api_key:
        lines.append(f"GEMINI_API_KEY={data.api_key}")
    if "model" not in keys_found:
        lines.append(f"GEMINI_MODEL={data.model_name}")

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Update in-memory settings
    settings.gemini_api_base_url = data.api_base_url
    if "****" not in data.api_key:
        settings.gemini_api_key = data.api_key
    settings.gemini_model = data.model_name

    return {"message": "Settings saved"}
