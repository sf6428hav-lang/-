import os
import pytest
from pathlib import Path

# Set test environment before importing app
os.environ["GEMINI_API_KEY"] = "test-key-for-testing"
os.environ["GEMINI_API_BASE_URL"] = "https://test.example.com"

@pytest.fixture
async def test_app(tmp_path):
    from app.config import settings
    original_db = settings.db_path
    original_data = settings.data_dir
    original_scripts = settings.scripts_dir
    original_downloads = settings.downloads_dir

    settings.data_dir = tmp_path / "data"
    settings.scripts_dir = tmp_path / "data" / "scripts"
    settings.downloads_dir = tmp_path / "downloads"
    settings.db_path = tmp_path / "data" / "test.sqlite"
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.scripts_dir.mkdir(parents=True, exist_ok=True)
    settings.downloads_dir.mkdir(parents=True, exist_ok=True)

    from app.database import init_db
    await init_db()

    from app.main import app
    yield app

    settings.db_path = original_db
    settings.data_dir = original_data
    settings.scripts_dir = original_scripts
    settings.downloads_dir = original_downloads


@pytest.fixture
async def client(test_app):
    from httpx import AsyncClient, ASGITransport
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
