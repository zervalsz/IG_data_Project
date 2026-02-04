"""
Minimal Instagram control endpoints
- POST /api/instagram/fetch   -> schedule a background fetch (+ optional analyze)
- GET  /api/instagram/health  -> run pipeline diagnostics

This file is intentionally small and calls into the existing collectors/instagram code
without modifying the collector code.
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

router = APIRouter(prefix="/api/instagram", tags=["instagram"])


class FetchRequest(BaseModel):
    username: str
    post_pages: int = 2
    reel_pages: int = 2
    page_count: int = 12
    store_local_first: bool = False
    local_file_limit: Optional[int] = 5
    analyze: bool = False


def _ensure_repo_in_path():
    """Ensure project root is on sys.path so we can import collectors modules."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


@router.get("/health")
async def health_check():
    _ensure_repo_in_path()
    try:
        from collectors.instagram.pipeline import run_diagnostics
        res = run_diagnostics()
        return {"ok": True, "diagnostics": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnostics failed: {e}")


@router.post("/fetch")
async def fetch_instagram(req: FetchRequest, background_tasks: BackgroundTasks):
    """Schedule a background task to fetch pages for `req.username`.

    This keeps the endpoint fast and non-blocking. The background task will call
    into collectors/instagram/fetcher.py and optionally run analysis via
    collectors/instagram/pipeline.process_instagram_user.
    """
    _ensure_repo_in_path()
    try:
        from collectors.instagram.fetcher import fetch_and_store_paged
        from collectors.instagram.pipeline import process_instagram_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import error: {e}")

    def _task():
        try:
            fetch_and_store_paged(
                req.username,
                post_pages=req.post_pages,
                reel_pages=req.reel_pages,
                count=req.page_count,
                store_local_first=req.store_local_first,
                local_file_limit=req.local_file_limit,
                upload_after_local=True,
            )
            if req.analyze:
                # process_instagram_user accepts a `user_id` argument (we use the username)
                process_instagram_user(req.username)
        except Exception:
            # We intentionally print the traceback so it's available in logs
            import traceback
            traceback.print_exc()

    background_tasks.add_task(_task)
    return {"status": "scheduled", "username": req.username}
