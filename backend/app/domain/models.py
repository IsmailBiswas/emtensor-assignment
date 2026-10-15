from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

PersonStatus = Literal["active", "on_leave", "exited"]
TaskStatus = Literal["not_started", "in_progress", "completed"]
ComponentStatus = Literal[
    "planned",
    "ordered",
    "delivered",
    "in_progress",
    "installed",
    "tested",
]
ComponentType = Literal[
    "system",
    "subsystem",
    "assembly",
    "unit",
    "sub_unit",
    "part",
]
ExpenseCategory = Literal[
    "equipment",
    "civil_works",
    "consumables",
    "manpower",
    "travel",
    "software_licences",
    "contingency",
]
ComponentDependencyType = Literal[
    "enclosure",
    "physical_space",
    "platform",
    "power",
    "telemetry",
]


class Department(BaseModel):
    dept_id: str
    dept_name: str
    scope: str
    total_budget_inr: float
    head_researcher_id: str


class Researcher(BaseModel):
    researcher_id: str
    full_name: str
    dept_id: str
    role: str
    email: str
    project_allocation_pct: float
    monthly_cost_inr: float
    joined_on: date | None
    left_on: date | None
    status: str
    joined_on_raw: str | None = None
    left_on_raw: str | None = None


class FundingTranche(BaseModel):
    tranche_id: str
    pct_of_grant: float
    amount_inr: float
    condition_milestone_id: str
    expected_release: date | None
    actual_release: date | None
    status: str
    expected_release_raw: str | None = None
    actual_release_raw: str | None = None


class BudgetAllocation(BaseModel):
    allocation_id: str
    dept_id: str
    category: str
    tranche_id: str
    amount_inr: float


class WorkPackage(BaseModel):
    task_id: str
    parent_task_id: str | None
    dept_id: str
    task_name: str
    component_id: str | None
    owner_researcher_id: str | None
    planned_start: date | None
    planned_end: date | None
    actual_start: date | None
    actual_end: date | None
    status: str
    planned_start_raw: str | None = None
    planned_end_raw: str | None = None
    actual_start_raw: str | None = None
    actual_end_raw: str | None = None

    @property
    def is_work_package_root(self) -> bool:
        return self.task_id.startswith("WP-")


class TaskDependency(BaseModel):
    predecessor_task_id: str
    successor_task_id: str
    dependency_type: str
    lag_days: int


class Milestone(BaseModel):
    milestone_id: str
    milestone_name: str
    due_date: date | None
    linked_task_ids: list[str] = Field(default_factory=list)
    releases_tranche_id: str | None
    reported_status: str
    due_date_raw: str | None = None


class ProgressUpdate(BaseModel):
    update_id: str
    task_id: str
    report_date: date | None
    percent_complete: float
    reported_by: str | None
    blocker: str | None
    note: str | None
    report_date_raw: str | None = None


class Component(BaseModel):
    component_id: str
    parent_component_id: str | None
    component_name: str
    component_type: str
    owner_dept_id: str | None
    quantity: float
    unit_cost_inr: float
    governing_task_id: str | None
    status: str


class ComponentDependency(BaseModel):
    component_id: str
    depends_on_component_id: str
    dependency_type: str


class PurchaseOrder(BaseModel):
    po_id: str
    dept_id: str
    vendor: str
    component_id: str | None
    category: str
    po_amount_inr: float
    order_date: date | None
    expected_delivery: date | None
    actual_delivery: date | None
    po_status: str
    order_date_raw: str | None = None
    expected_delivery_raw: str | None = None
    actual_delivery_raw: str | None = None


class Expenditure(BaseModel):
    expense_id: str
    dept_id: str
    allocation_id: str
    category: str
    po_id: str | None
    vendor: str | None
    amount_inr: float
    expense_date: date | None
    description: str | None
    invoice_no: str | None
    requested_by: str | None
    approved_by: str | None
    expense_date_raw: str | None = None


class Timesheet(BaseModel):
    researcher_id: str
    week_start: date | None
    task_id: str | None
    activity: str | None
    hours: float
    week_start_raw: str | None = None
