import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_base_url: str = "https://generativelanguage.googleapis.com"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-pro"
    port: int = 8000
    
    # Paths
    data_dir: Path = Path(__file__).parent.parent / "data"
    scripts_dir: Path = data_dir / "scripts"
    downloads_dir: Path = Path(__file__).parent.parent / "downloads"
    static_dir: Path = Path(__file__).parent.parent / "static"
    db_path: Path = data_dir / "database.sqlite"
    
    model_config = {
        "env_file": str(Path(__file__).parent.parent / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

settings = Settings()

# Ensure directories exist
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.scripts_dir.mkdir(parents=True, exist_ok=True)
settings.downloads_dir.mkdir(parents=True, exist_ok=True)
settings.static_dir.mkdir(parents=True, exist_ok=True)
