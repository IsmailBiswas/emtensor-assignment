from datetime import date

from pydantic import BaseModel


class LinkedTaskStatus(BaseModel):
    task_id: str
    task_name: str
    dept_id: str
    status: str
    planned_end: date | None
    actual_end: date | None
    blocker_count: int
    open_predecessors: list[str]


class MilestoneDetail(BaseModel):
    milestone_id: str
    milestone_name: str
    due_date: date | None
    days_to_due: int | None
    reported_status: str
    computed_status: str
    releases_tranche_id: str | None
    linked_tasks: list[LinkedTaskStatus]
    linked_tasks_completed: int
    linked_tasks_total: int
    open_blocker_task_ids: list[str]
    explanation: str


class TrancheDetail(BaseModel):
    tranche_id: str
    pct_of_grant: float
    amount_inr: float
    status: str
    condition_milestone_id: str
    expected_release: date | None
    actual_release: date | None
    days_to_expected: int | None
    risk: str
    risk_explanation: str


class DeadlineItem(BaseModel):
    kind: str
    id: str
    name: str
    due_date: date
    days_to_due: int
    status: str
    detail: str


class ProgressResponse(BaseModel):
    as_of: date
    milestones: list[MilestoneDetail]
    tranches: list[TrancheDetail]
    upcoming_deadlines: list[DeadlineItem]
    overdue_deadlines: list[DeadlineItem]
