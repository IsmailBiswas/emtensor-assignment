from fastapi import APIRouter, Depends

from app.api.deps import get_health_checker
from app.interfaces.health import HealthChecker, HealthStatus

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthStatus)
async def health(checker: HealthChecker = Depends(get_health_checker)) -> HealthStatus:
    return await checker.check()
