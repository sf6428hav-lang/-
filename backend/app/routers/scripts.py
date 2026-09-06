import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse, FileResponse
import aiosqlite

from ..config import settings
from ..models import GenerateRequest, ScriptResponse, ScriptRecord
from ..services.parser import parse_link, detect_platform
from ..services.downloader import download_video, cleanup_video
from ..services.gemini_worker import generate_script
from ..services.doc_generator import generate_docx, generate_txt

router = APIRouter(prefix="/api", tags=["scripts"])


@router.post("/generate")
async def generate_scripts(request: GenerateRequest):
    """Generate scripts from video links using SSE."""

    async def event_generator():
        records = []
        for idx, link in enumerate(request.links):
            record_id = str(uuid.uuid4())
            try:
                # Parse
                yield _sse({"type": "progress", "index": idx, "status": "parsing", "message": f"Parsing link {idx+1}..."})
                parsed = await parse_link(link)

                # Download
                yield _sse({"type": "progress", "index": idx, "status": "downloading", "message": "Downloading video..."})
                ext = ".mp4"
                filename = f"{record_id}{ext}"
                video_path = await download_video(parsed.video_url, filename)

                # Generate
                yield _sse({"type": "progress", "index": idx, "status": "generating", "message": "Generating script with Gemini..."})
                script_text = generate_script(video_path)

                # Save
                script_file = settings.scripts_dir / f"{record_id}.txt"
                script_file.write_text(script_text, encoding="utf-8")

                title = parsed.title or f"Script {idx+1}"
                created = datetime.now().isoformat()

                async with aiosqlite.connect(settings.db_path) as db:
                    await db.execute(
                        "INSERT INTO scripts (id, title, type, links, output, created_at, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (record_id, title, "single", json.dumps([link]), script_text, created, "done")
                    )
                    await db.commit()

                records.append({"id": record_id, "title": title, "status": "done"})
                yield _sse({"type": "progress", "index": idx, "status": "done", "message": "Complete"})

                # Cleanup video
                cleanup_video(video_path)

            except Exception as e:
                records.append({"id": record_id, "title": link[:50], "status": "failed", "error": str(e)})
                yield _sse({"type": "progress", "index": idx, "status": "failed", "message": str(e)})

        yield _sse({"type": "complete", "records": records})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/scripts/{script_id}")
async def get_script(script_id: str):
    """Get a script by ID."""
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM scripts WHERE id = ?", (script_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Script not found")
        return {
            "id": row["id"],
            "title": row["title"],
            "type": row["type"],
            "links": json.loads(row["links"]),
            "output": row["output"],
            "created_at": row["created_at"],
            "status": row["status"],
        }


@router.get("/scripts/{script_id}/download")
async def download_script(script_id: str, format: str = Query(default="txt", pattern="^(docx|txt)$")):
    """Download a script in the specified format."""
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM scripts WHERE id = ?", (script_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Script not found")

    title = row["title"]
    content = row["output"]
    safe_title = "".join(c for c in title if c.isalnum() or c in " _-").strip() or "script"

    if format == "docx":
        output_path = settings.downloads_dir / f"{script_id}.docx"
        generate_docx(content, title, output_path)
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"{safe_title}.docx",
        )
    else:
        output_path = settings.downloads_dir / f"{script_id}.txt"
        output_path.write_text(content, encoding="utf-8")
        return FileResponse(output_path, media_type="text/plain", filename=f"{safe_title}.txt")


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
