from pydantic import BaseModel


class Anomaly(BaseModel):
    id: str
    rule: str
    severity: str
    title: str
    explanation: str
    entity_type: str
    entity_id: str


class AnomaliesResponse(BaseModel):
    as_of: str
    total: int
    by_severity: dict[str, int]
    by_rule: dict[str, int]
    items: list[Anomaly]
