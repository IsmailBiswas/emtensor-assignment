import asyncio

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_project_store
from app.api.schemas.overview import OverviewResponse
from app.interfaces.project_store import ProjectStore
from app.services.overview import build_overview

router = APIRouter(tags=["overview"])


@router.get("/overview", response_model=OverviewResponse)
async def get_overview(store: ProjectStore = Depends(get_project_store)) -> OverviewResponse:
    try:
        dataset = store.get()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return await asyncio.to_thread(build_overview, dataset)
