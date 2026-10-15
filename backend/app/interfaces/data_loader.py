from typing import Protocol

from app.domain.dataset import ProjectDataset


class ProjectDataLoader(Protocol):
    """Loads the project CSV snapshot into an in-memory dataset."""

    def load(self) -> ProjectDataset: ...
