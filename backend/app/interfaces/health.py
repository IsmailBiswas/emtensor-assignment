from typing import Protocol

from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str
    service: str


class HealthChecker(Protocol):
    async def check(self) -> HealthStatus: ...
