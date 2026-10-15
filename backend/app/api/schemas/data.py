from datetime import date, datetime

from pydantic import BaseModel


class DatasetSummary(BaseModel):
    as_of: date
    loaded_at: datetime
    counts: dict[str, int]


class ReloadResponse(BaseModel):
    status: str
    summary: DatasetSummary
