from typing import Protocol

from app.domain.dataset import ProjectDataset


class ProjectStore(Protocol):
    """Holds the current in-memory project dataset and supports reload."""

    def get(self) -> ProjectDataset: ...

    async def reload(self) -> ProjectDataset: ...
