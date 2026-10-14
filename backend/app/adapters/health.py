from app.core.config import settings
from app.interfaces.health import HealthStatus


class StaticHealthChecker:
    async def check(self) -> HealthStatus:
        return HealthStatus(status="ok", service=settings.app_name)
