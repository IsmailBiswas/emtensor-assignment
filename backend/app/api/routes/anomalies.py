import asyncio

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_project_store
from app.api.schemas.anomalies import AnomaliesResponse
from app.interfaces.project_store import ProjectStore
from app.services.anomalies import detect_anomalies

router = APIRouter(tags=["anomalies"])


@router.get("/anomalies", response_model=AnomaliesResponse)
async def get_anomalies(store: ProjectStore = Depends(get_project_store)) -> AnomaliesResponse:
    try:
        dataset = store.get()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return await asyncio.to_thread(detect_anomalies, dataset)
