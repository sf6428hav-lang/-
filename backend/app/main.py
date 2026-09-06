import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import settings
from .database import init_db
from .routers import scripts, history, settings as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print(f"Database initialized at {settings.db_path}")
    print(f"Static files directory: {settings.static_dir}")
    yield
    # Shutdown
    print("Application shutting down")


app = FastAPI(
    title="短剧剧本生成器",
    description="自动解析短剧视频并生成《麻将声》格式分场剧本",
    version="1.0.0",
    lifespan=lifespan,
)

# Include API routers
app.include_router(scripts.router)
app.include_router(history.router)
app.include_router(settings_router.router)

# Serve static files
static_dir = settings.static_dir
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    @app.get("/")
    async def root():
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"message": "Short Drama Script Generator API", "docs": "/docs"}
else:
    print(f"Warning: Static directory not found at {static_dir}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        workers=1,
    )
