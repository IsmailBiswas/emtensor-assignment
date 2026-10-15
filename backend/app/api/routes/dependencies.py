import asyncio

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_project_store
from app.api.schemas.dependencies import DependencyGraphResponse, PeopleResponse
from app.interfaces.project_store import ProjectStore
from app.services.dependencies import (
    build_component_dependency_graph,
    build_people,
    build_task_dependency_graph,
)

router = APIRouter(tags=["dependencies"])


@router.get("/dependencies/tasks", response_model=DependencyGraphResponse)
async def task_dependencies(
    store: ProjectStore = Depends(get_project_store),
) -> DependencyGraphResponse:
    try:
        dataset = store.get()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return await asyncio.to_thread(build_task_dependency_graph, dataset)


@router.get("/dependencies/components", response_model=DependencyGraphResponse)
async def component_dependencies(
    store: ProjectStore = Depends(get_project_store),
) -> DependencyGraphResponse:
    try:
        dataset = store.get()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return await asyncio.to_thread(build_component_dependency_graph, dataset)


@router.get("/people", response_model=PeopleResponse)
async def people(store: ProjectStore = Depends(get_project_store)) -> PeopleResponse:
    try:
        dataset = store.get()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return await asyncio.to_thread(build_people, dataset)
