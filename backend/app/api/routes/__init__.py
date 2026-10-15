from fastapi import APIRouter

from app.api.routes import anomalies, data, dependencies, health, overview, progress

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(data.router)
api_router.include_router(overview.router)
api_router.include_router(progress.router)
api_router.include_router(anomalies.router)
api_router.include_router(dependencies.router)
