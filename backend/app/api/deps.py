from functools import lru_cache

from app.adapters.health import StaticHealthChecker
from app.interfaces.health import HealthChecker


@lru_cache
def get_health_checker() -> HealthChecker:
    return StaticHealthChecker()
