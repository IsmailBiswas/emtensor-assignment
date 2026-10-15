from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from app.domain.dataset import ProjectDataset, utc_now
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
from app.domain.parsing import (
    empty_to_none,
    parse_float,
    parse_int,
    parse_optional_date,
    parse_optional_float,
    split_semicolon_ids,
)

REQUIRED_FILES = (
    "departments.csv",
    "researchers.csv",
    "funding_tranches.csv",
    "budget_allocations.csv",
    "work_packages.csv",
    "task_dependencies.csv",
    "milestones.csv",
    "progress_updates.csv",
    "components.csv",
    "component_dependencies.csv",
    "purchase_orders.csv",
    "expenditures.csv",
    "timesheets.csv",
)


class CsvProjectDataLoader:
    """Parses assignment CSVs from disk into a ProjectDataset (blocking I/O)."""

    def __init__(self, data_dir: str | Path, *, as_of: date) -> None:
        self._data_dir = Path(data_dir)
        self._as_of = as_of

    def load(self) -> ProjectDataset:
        if not self._data_dir.is_dir():
            raise FileNotFoundError(f"Data directory not found: {self._data_dir}")

        missing = [name for name in REQUIRED_FILES if not (self._data_dir / name).is_file()]
        if missing:
            raise FileNotFoundError(
                f"Missing required CSV files in {self._data_dir}: {', '.join(missing)}"
            )

        dataset = ProjectDataset(
            as_of=self._as_of,
            loaded_at=utc_now(),
            departments=self._load_departments(),
            researchers=self._load_researchers(),
            funding_tranches=self._load_tranches(),
            budget_allocations=self._load_allocations(),
            work_packages=self._load_work_packages(),
            task_dependencies=self._load_task_dependencies(),
            milestones=self._load_milestones(),
            progress_updates=self._load_progress_updates(),
            components=self._load_components(),
            component_dependencies=self._load_component_dependencies(),
            purchase_orders=self._load_purchase_orders(),
            expenditures=self._load_expenditures(),
            timesheets=self._load_timesheets(),
        )
        dataset.rebuild_indexes()
        return dataset

    def _read_rows(self, filename: str) -> list[dict[str, str]]:
        path = self._data_dir / filename
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def _load_departments(self) -> list[Department]:
        return [
            Department(
                dept_id=row["dept_id"].strip(),
                dept_name=row["dept_name"].strip(),
                scope=row.get("scope", "").strip(),
                total_budget_inr=parse_float(row.get("total_budget_inr"), field="total_budget_inr"),
                head_researcher_id=row["head_researcher_id"].strip(),
            )
            for row in self._read_rows("departments.csv")
        ]

    def _load_researchers(self) -> list[Researcher]:
        rows: list[Researcher] = []
        for row in self._read_rows("researchers.csv"):
            joined_raw = empty_to_none(row.get("joined_on"))
            left_raw = empty_to_none(row.get("left_on"))
            rows.append(
                Researcher(
                    researcher_id=row["researcher_id"].strip(),
                    full_name=row["full_name"].strip(),
                    dept_id=row["dept_id"].strip(),
                    role=row["role"].strip(),
                    email=row.get("email", "").strip(),
                    project_allocation_pct=parse_float(
                        row.get("project_allocation_pct"),
                        field="project_allocation_pct",
                    ),
                    monthly_cost_inr=parse_float(
                        row.get("monthly_cost_inr"),
                        field="monthly_cost_inr",
                    ),
                    joined_on=parse_optional_date(joined_raw),
                    left_on=parse_optional_date(left_raw),
                    status=row["status"].strip(),
                    joined_on_raw=joined_raw,
                    left_on_raw=left_raw,
                )
            )
        return rows

    def _load_tranches(self) -> list[FundingTranche]:
        rows: list[FundingTranche] = []
        for row in self._read_rows("funding_tranches.csv"):
            expected_raw = empty_to_none(row.get("expected_release"))
            actual_raw = empty_to_none(row.get("actual_release"))
            rows.append(
                FundingTranche(
                    tranche_id=row["tranche_id"].strip(),
                    pct_of_grant=parse_float(row.get("pct_of_grant"), field="pct_of_grant"),
                    amount_inr=parse_float(row.get("amount_inr"), field="amount_inr"),
                    condition_milestone_id=row["condition_milestone_id"].strip(),
                    expected_release=parse_optional_date(expected_raw),
                    actual_release=parse_optional_date(actual_raw),
                    status=row["status"].strip(),
                    expected_release_raw=expected_raw,
                    actual_release_raw=actual_raw,
                )
            )
        return rows

    def _load_allocations(self) -> list[BudgetAllocation]:
        return [
            BudgetAllocation(
                allocation_id=row["allocation_id"].strip(),
                dept_id=row["dept_id"].strip(),
                category=row["category"].strip(),
                tranche_id=row["tranche_id"].strip(),
                amount_inr=parse_float(row.get("amount_inr"), field="amount_inr"),
            )
            for row in self._read_rows("budget_allocations.csv")
        ]

    def _load_work_packages(self) -> list[WorkPackage]:
        rows: list[WorkPackage] = []
        for row in self._read_rows("work_packages.csv"):
            planned_start_raw = empty_to_none(row.get("planned_start"))
            planned_end_raw = empty_to_none(row.get("planned_end"))
            actual_start_raw = empty_to_none(row.get("actual_start"))
            actual_end_raw = empty_to_none(row.get("actual_end"))
            rows.append(
                WorkPackage(
                    task_id=row["task_id"].strip(),
                    parent_task_id=empty_to_none(row.get("parent_task_id")),
                    dept_id=row["dept_id"].strip(),
                    task_name=row["task_name"].strip(),
                    component_id=empty_to_none(row.get("component_id")),
                    owner_researcher_id=empty_to_none(row.get("owner_researcher_id")),
                    planned_start=parse_optional_date(planned_start_raw),
                    planned_end=parse_optional_date(planned_end_raw),
                    actual_start=parse_optional_date(actual_start_raw),
                    actual_end=parse_optional_date(actual_end_raw),
                    status=(empty_to_none(row.get("status")) or ""),
                    planned_start_raw=planned_start_raw,
                    planned_end_raw=planned_end_raw,
                    actual_start_raw=actual_start_raw,
                    actual_end_raw=actual_end_raw,
                )
            )
        return rows

    def _load_task_dependencies(self) -> list[TaskDependency]:
        return [
            TaskDependency(
                predecessor_task_id=row["predecessor_task_id"].strip(),
                successor_task_id=row["successor_task_id"].strip(),
                dependency_type=row.get("dependency_type", "").strip(),
                lag_days=parse_int(row.get("lag_days"), field="lag_days"),
            )
            for row in self._read_rows("task_dependencies.csv")
        ]

    def _load_milestones(self) -> list[Milestone]:
        rows: list[Milestone] = []
        for row in self._read_rows("milestones.csv"):
            due_raw = empty_to_none(row.get("due_date"))
            rows.append(
                Milestone(
                    milestone_id=row["milestone_id"].strip(),
                    milestone_name=row["milestone_name"].strip(),
                    due_date=parse_optional_date(due_raw),
                    linked_task_ids=split_semicolon_ids(row.get("linked_task_ids")),
                    releases_tranche_id=empty_to_none(row.get("releases_tranche_id")),
                    reported_status=row["reported_status"].strip(),
                    due_date_raw=due_raw,
                )
            )
        return rows

    def _load_progress_updates(self) -> list[ProgressUpdate]:
        rows: list[ProgressUpdate] = []
        for row in self._read_rows("progress_updates.csv"):
            report_raw = empty_to_none(row.get("report_date"))
            rows.append(
                ProgressUpdate(
                    update_id=row["update_id"].strip(),
                    task_id=row["task_id"].strip(),
                    report_date=parse_optional_date(report_raw),
                    percent_complete=parse_float(
                        row.get("percent_complete"),
                        field="percent_complete",
                    ),
                    reported_by=empty_to_none(row.get("reported_by")),
                    blocker=empty_to_none(row.get("blocker")),
                    note=empty_to_none(row.get("note")),
                    report_date_raw=report_raw,
                )
            )
        return rows

    def _load_components(self) -> list[Component]:
        return [
            Component(
                component_id=row["component_id"].strip(),
                parent_component_id=empty_to_none(row.get("parent_component_id")),
                component_name=row["component_name"].strip(),
                component_type=row["component_type"].strip(),
                owner_dept_id=empty_to_none(row.get("owner_dept_id")),
                quantity=parse_float(row.get("quantity"), field="quantity"),
                unit_cost_inr=parse_float(row.get("unit_cost_inr"), field="unit_cost_inr"),
                governing_task_id=empty_to_none(row.get("governing_task_id")),
                status=row["status"].strip(),
            )
            for row in self._read_rows("components.csv")
        ]

    def _load_component_dependencies(self) -> list[ComponentDependency]:
        return [
            ComponentDependency(
                component_id=row["component_id"].strip(),
                depends_on_component_id=row["depends_on_component_id"].strip(),
                dependency_type=row["dependency_type"].strip(),
            )
            for row in self._read_rows("component_dependencies.csv")
        ]

    def _load_purchase_orders(self) -> list[PurchaseOrder]:
        rows: list[PurchaseOrder] = []
        for row in self._read_rows("purchase_orders.csv"):
            order_raw = empty_to_none(row.get("order_date"))
            expected_raw = empty_to_none(row.get("expected_delivery"))
            actual_raw = empty_to_none(row.get("actual_delivery"))
            rows.append(
                PurchaseOrder(
                    po_id=row["po_id"].strip(),
                    dept_id=row["dept_id"].strip(),
                    vendor=row.get("vendor", "").strip(),
                    component_id=empty_to_none(row.get("component_id")),
                    category=row.get("category", "").strip(),
                    po_amount_inr=parse_float(row.get("po_amount_inr"), field="po_amount_inr"),
                    order_date=parse_optional_date(order_raw),
                    expected_delivery=parse_optional_date(expected_raw),
                    actual_delivery=parse_optional_date(actual_raw),
                    po_status=row.get("po_status", "").strip(),
                    order_date_raw=order_raw,
                    expected_delivery_raw=expected_raw,
                    actual_delivery_raw=actual_raw,
                )
            )
        return rows

    def _load_expenditures(self) -> list[Expenditure]:
        rows: list[Expenditure] = []
        for row in self._read_rows("expenditures.csv"):
            date_raw = empty_to_none(row.get("expense_date"))
            rows.append(
                Expenditure(
                    expense_id=row["expense_id"].strip(),
                    dept_id=row["dept_id"].strip(),
                    allocation_id=row["allocation_id"].strip(),
                    category=row["category"].strip(),
                    po_id=empty_to_none(row.get("po_id")),
                    vendor=empty_to_none(row.get("vendor")),
                    amount_inr=parse_float(row.get("amount_inr"), field="amount_inr"),
                    expense_date=parse_optional_date(date_raw),
                    description=empty_to_none(row.get("description")),
                    invoice_no=empty_to_none(row.get("invoice_no")),
                    requested_by=empty_to_none(row.get("requested_by")),
                    approved_by=empty_to_none(row.get("approved_by")),
                    expense_date_raw=date_raw,
                )
            )
        return rows

    def _load_timesheets(self) -> list[Timesheet]:
        rows: list[Timesheet] = []
        for row in self._read_rows("timesheets.csv"):
            week_raw = empty_to_none(row.get("week_start"))
            hours = parse_optional_float(row.get("hours"))
            if hours is None:
                raise ValueError(f"Missing hours for timesheet {row}")
            rows.append(
                Timesheet(
                    researcher_id=row["researcher_id"].strip(),
                    week_start=parse_optional_date(week_raw),
                    task_id=empty_to_none(row.get("task_id")),
                    activity=empty_to_none(row.get("activity")),
                    hours=hours,
                    week_start_raw=week_raw,
                )
            )
        return rows
