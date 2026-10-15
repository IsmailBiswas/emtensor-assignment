from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str
    group: str
    status: str
    detail: str
    level: int


class GraphEdge(BaseModel):
    source: str
    target: str
    kind: str
    label: str


class DependencyGraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    levels: list[list[str]]


class PeoplePerson(BaseModel):
    researcher_id: str
    full_name: str
    dept_id: str
    role: str
    status: str
    project_allocation_pct: float
    email: str


class PeopleResponse(BaseModel):
    total: int
    people: list[PeoplePerson]
