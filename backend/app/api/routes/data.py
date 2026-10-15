from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_project_store
from app.api.schemas.data import DatasetSummary, ReloadResponse
from app.interfaces.project_store import ProjectStore

router = APIRouter(tags=["data"])


def _summary_from_store(store: ProjectStore) -> DatasetSummary:
    dataset = store.get()
    return DatasetSummary(
        as_of=dataset.as_of,
        loaded_at=dataset.loaded_at,
        counts=dataset.summary_counts(),
    )


@router.get("/data/summary", response_model=DatasetSummary)
async def data_summary(store: ProjectStore = Depends(get_project_store)) -> DatasetSummary:
    try:
        return _summary_from_store(store)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/data/refresh", response_model=ReloadResponse)
async def refresh_data(store: ProjectStore = Depends(get_project_store)) -> ReloadResponse:
    try:
        await store.reload()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - surface load failures clearly
        raise HTTPException(status_code=500, detail=f"Failed to reload data: {exc}") from exc
    return ReloadResponse(status="reloaded", summary=_summary_from_store(store))
