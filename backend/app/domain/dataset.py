from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from app.domain.models import (
    BudgetAllocation,
    Component,
    ComponentDependency,
    Department,
    Expenditure,
    FundingTranche,
    Milestone,
    ProgressUpdate,
    PurchaseOrder,
    Researcher,
    TaskDependency,
    Timesheet,
    WorkPackage,
)


@dataclass
class ProjectDataset:
    """In-memory project snapshot: rows plus lookup indexes and adjacency lists."""

    as_of: date
    loaded_at: datetime
    departments: list[Department]
    researchers: list[Researcher]
    funding_tranches: list[FundingTranche]
    budget_allocations: list[BudgetAllocation]
    work_packages: list[WorkPackage]
    task_dependencies: list[TaskDependency]
    milestones: list[Milestone]
    progress_updates: list[ProgressUpdate]
    components: list[Component]
    component_dependencies: list[ComponentDependency]
    purchase_orders: list[PurchaseOrder]
    expenditures: list[Expenditure]
    timesheets: list[Timesheet]

    departments_by_id: dict[str, Department] = field(default_factory=dict)
    researchers_by_id: dict[str, Researcher] = field(default_factory=dict)
    tranches_by_id: dict[str, FundingTranche] = field(default_factory=dict)
    allocations_by_id: dict[str, BudgetAllocation] = field(default_factory=dict)
    tasks_by_id: dict[str, WorkPackage] = field(default_factory=dict)
    milestones_by_id: dict[str, Milestone] = field(default_factory=dict)
    components_by_id: dict[str, Component] = field(default_factory=dict)
    purchase_orders_by_id: dict[str, PurchaseOrder] = field(default_factory=dict)
    expenditures_by_id: dict[str, Expenditure] = field(default_factory=dict)

    researchers_by_dept: dict[str, list[Researcher]] = field(default_factory=dict)
    tasks_by_dept: dict[str, list[WorkPackage]] = field(default_factory=dict)
    allocations_by_dept: dict[str, list[BudgetAllocation]] = field(default_factory=dict)
    allocations_by_tranche: dict[str, list[BudgetAllocation]] = field(default_factory=dict)
    expenditures_by_allocation: dict[str, list[Expenditure]] = field(default_factory=dict)
    expenditures_by_po: dict[str, list[Expenditure]] = field(default_factory=dict)
    progress_by_task: dict[str, list[ProgressUpdate]] = field(default_factory=dict)
    timesheets_by_researcher: dict[str, list[Timesheet]] = field(default_factory=dict)
    component_children: dict[str, list[Component]] = field(default_factory=dict)

    # Task adjacency: predecessor -> successors (outgoing), successor -> predecessors (incoming)
    task_successors: dict[str, list[str]] = field(default_factory=dict)
    task_predecessors: dict[str, list[str]] = field(default_factory=dict)

    # Component adjacency: component -> dependencies it needs (outgoing needs),
    # and reverse: dependency -> components that need it
    component_depends_on: dict[str, list[str]] = field(default_factory=dict)
    component_required_by: dict[str, list[str]] = field(default_factory=dict)

    tranche_by_condition_milestone: dict[str, FundingTranche] = field(default_factory=dict)
    milestone_by_released_tranche: dict[str, Milestone] = field(default_factory=dict)

    def rebuild_indexes(self) -> None:
        self.departments_by_id = {d.dept_id: d for d in self.departments}
        self.researchers_by_id = {r.researcher_id: r for r in self.researchers}
        self.tranches_by_id = {t.tranche_id: t for t in self.funding_tranches}
        self.allocations_by_id = {a.allocation_id: a for a in self.budget_allocations}
        self.tasks_by_id = {t.task_id: t for t in self.work_packages}
        self.milestones_by_id = {m.milestone_id: m for m in self.milestones}
        self.components_by_id = {c.component_id: c for c in self.components}
        self.purchase_orders_by_id = {p.po_id: p for p in self.purchase_orders}
        self.expenditures_by_id = {e.expense_id: e for e in self.expenditures}

        self.researchers_by_dept = _group(self.researchers, lambda r: r.dept_id)
        self.tasks_by_dept = _group(self.work_packages, lambda t: t.dept_id)
        self.allocations_by_dept = _group(self.budget_allocations, lambda a: a.dept_id)
        self.allocations_by_tranche = _group(self.budget_allocations, lambda a: a.tranche_id)
        self.expenditures_by_allocation = _group(
            self.expenditures, lambda e: e.allocation_id
        )
        self.expenditures_by_po = _group(
            [e for e in self.expenditures if e.po_id],
            lambda e: e.po_id or "",
        )
        self.progress_by_task = _group(self.progress_updates, lambda p: p.task_id)
        self.timesheets_by_researcher = _group(
            self.timesheets, lambda t: t.researcher_id
        )
        self.component_children = _group(
            [c for c in self.components if c.parent_component_id],
            lambda c: c.parent_component_id or "",
        )

        successors: dict[str, list[str]] = defaultdict(list)
        predecessors: dict[str, list[str]] = defaultdict(list)
        for dep in self.task_dependencies:
            successors[dep.predecessor_task_id].append(dep.successor_task_id)
            predecessors[dep.successor_task_id].append(dep.predecessor_task_id)
        self.task_successors = dict(successors)
        self.task_predecessors = dict(predecessors)

        depends_on: dict[str, list[str]] = defaultdict(list)
        required_by: dict[str, list[str]] = defaultdict(list)
        for dep in self.component_dependencies:
            depends_on[dep.component_id].append(dep.depends_on_component_id)
            required_by[dep.depends_on_component_id].append(dep.component_id)
        self.component_depends_on = dict(depends_on)
        self.component_required_by = dict(required_by)

        self.tranche_by_condition_milestone = {
            t.condition_milestone_id: t
            for t in self.funding_tranches
            if t.condition_milestone_id
        }
        self.milestone_by_released_tranche = {
            m.releases_tranche_id: m
            for m in self.milestones
            if m.releases_tranche_id
        }

    def summary_counts(self) -> dict[str, int]:
        return {
            "departments": len(self.departments),
            "researchers": len(self.researchers),
            "funding_tranches": len(self.funding_tranches),
            "budget_allocations": len(self.budget_allocations),
            "work_packages": len(self.work_packages),
            "task_dependencies": len(self.task_dependencies),
            "milestones": len(self.milestones),
            "progress_updates": len(self.progress_updates),
            "components": len(self.components),
            "component_dependencies": len(self.component_dependencies),
            "purchase_orders": len(self.purchase_orders),
            "expenditures": len(self.expenditures),
            "timesheets": len(self.timesheets),
        }


def _group(items: list, key_fn) -> dict[str, list]:
    grouped: dict[str, list] = defaultdict(list)
    for item in items:
        grouped[key_fn(item)].append(item)
    return dict(grouped)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
