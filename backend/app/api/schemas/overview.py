from datetime import date

from pydantic import BaseModel


class DepartmentSummary(BaseModel):
    dept_id: str
    dept_name: str
    total_budget_inr: float
    head_researcher_id: str
    staff_count: int
    task_count: int


class MilestoneSummary(BaseModel):
    milestone_id: str
    milestone_name: str
    due_date: date | None
    linked_task_ids: list[str]
    releases_tranche_id: str | None
    reported_status: str
    linked_tasks_completed: int
    linked_tasks_total: int


class TrancheSummary(BaseModel):
    tranche_id: str
    pct_of_grant: float
    amount_inr: float
    condition_milestone_id: str
    expected_release: date | None
    actual_release: date | None
    status: str


class OverviewResponse(BaseModel):
    as_of: date
    grant_total_inr: float
    grant_released_inr: float
    allocated_inr: float
    spent_inr: float
    people_active: int
    people_total: int
    departments: list[DepartmentSummary]
    milestones: list[MilestoneSummary]
    tranches: list[TrancheSummary]
    counts: dict[str, int]
