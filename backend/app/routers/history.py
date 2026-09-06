import json
from fastapi import APIRouter, HTTPException, Query
import aiosqlite

from ..config import settings

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
async def get_history(page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=100)):
    """Get generation history, newest first."""
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute("SELECT COUNT(*) as cnt FROM scripts")
        total = (await cursor.fetchone())["cnt"]
        
        offset = (page - 1) * page_size
        cursor = await db.execute(
            "SELECT * FROM scripts ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (page_size, offset)
        )
        rows = await cursor.fetchall()
        
        items = []
        for row in rows:
            items.append({
                "id": row["id"],
                "title": row["title"],
                "type": row["type"],
                "links": json.loads(row["links"]),
                "output": row["output"],
                "created_at": row["created_at"],
                "status": row["status"],
            })
        
        return {"items": items, "total": total}


@router.delete("/history/{script_id}")
async def delete_script(script_id: str):
    """Delete a script record and its files."""
    async with aiosqlite.connect(settings.db_path) as db:
        cursor = await db.execute("SELECT id FROM scripts WHERE id = ?", (script_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Script not found")
        
        await db.execute("DELETE FROM scripts WHERE id = ?", (script_id,))
        await db.commit()
    
    # Clean up files
    for ext in [".txt", ".docx"]:
        f = settings.scripts_dir / f"{script_id}{ext}"
        if f.exists():
            f.unlink()
        f = settings.downloads_dir / f"{script_id}{ext}"
        if f.exists():
            f.unlink()
    
    return {"message": "Deleted"}
