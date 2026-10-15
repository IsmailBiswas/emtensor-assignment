from functools import lru_cache

from app.adapters.csv_loader import CsvProjectDataLoader
from app.adapters.health import StaticHealthChecker
from app.adapters.in_memory_store import InMemoryProjectStore
from app.core.config import settings
from app.interfaces.data_loader import ProjectDataLoader
from app.interfaces.health import HealthChecker
from app.interfaces.project_store import ProjectStore


@lru_cache
def get_health_checker() -> HealthChecker:
    return StaticHealthChecker()


@lru_cache
def get_data_loader() -> ProjectDataLoader:
    return CsvProjectDataLoader(settings.data_dir, as_of=settings.as_of_date)


@lru_cache
def get_project_store() -> ProjectStore:
    return InMemoryProjectStore(get_data_loader())
