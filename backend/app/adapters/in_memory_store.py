from __future__ import annotations

import asyncio
from threading import Lock

from app.domain.dataset import ProjectDataset
from app.interfaces.data_loader import ProjectDataLoader


class InMemoryProjectStore:
    """Thread-safe holder for the loaded ProjectDataset."""

    def __init__(self, loader: ProjectDataLoader) -> None:
        self._loader = loader
        self._lock = Lock()
        self._dataset: ProjectDataset | None = None

    def get(self) -> ProjectDataset:
        with self._lock:
            if self._dataset is None:
                raise RuntimeError("Project dataset has not been loaded yet")
            return self._dataset

    def load_sync(self) -> ProjectDataset:
        dataset = self._loader.load()
        with self._lock:
            self._dataset = dataset
        return dataset

    async def reload(self) -> ProjectDataset:
        dataset = await asyncio.to_thread(self._loader.load)
        with self._lock:
            self._dataset = dataset
        return dataset
