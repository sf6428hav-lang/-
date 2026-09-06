import aiosqlite
from pathlib import Path
from .config import settings

async def init_db():
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS scripts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                type TEXT NOT NULL,
                links TEXT NOT NULL,
                output TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        await db.commit()

async def get_db():
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        yield db
