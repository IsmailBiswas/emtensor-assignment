import asyncio

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_project_store
from app.api.schemas.progress import ProgressResponse
from app.interfaces.project_store import ProjectStore
from app.services.progress import build_progress

router = APIRouter(tags=["progress"])


@router.get("/progress", response_model=ProgressResponse)
async def get_progress(store: ProjectStore = Depends(get_project_store)) -> ProgressResponse:
    try:
        dataset = store.get()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return await asyncio.to_thread(build_progress, dataset)
