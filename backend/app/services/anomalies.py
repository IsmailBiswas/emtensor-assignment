from __future__ import annotations

from collections import defaultdict
from datetime import date

from app.api.schemas.anomalies import AnomaliesResponse, Anomaly
from app.domain.dataset import ProjectDataset

PO_THRESHOLD = 500_000.0
COMPONENT_INSTALLED_RANK = {
    "planned": 0,
    "ordered": 1,
    "delivered": 2,
    "in_progress": 3,
    "installed": 4,
    "tested": 5,
}


def detect_anomalies(dataset: ProjectDataset) -> AnomaliesResponse:
    items: list[Anomaly] = []
    items.extend(_money_anomalies(dataset))
    items.extend(_people_anomalies(dataset))
    items.extend(_schedule_anomalies(dataset))
    items.extend(_component_anomalies(dataset))
    items.extend(_milestone_anomalies(dataset))
    items.extend(_timesheet_anomalies(dataset))

    by_severity: dict[str, int] = defaultdict(int)
    by_rule: dict[str, int] = defaultdict(int)
    for item in items:
        by_severity[item.severity] += 1
        by_rule[item.rule] += 1

    severity_order = {"high": 0, "medium": 1, "low": 2}
    items.sort(key=lambda a: (severity_order.get(a.severity, 9), a.rule, a.id))

    return AnomaliesResponse(
        as_of=dataset.as_of.isoformat(),
        total=len(items),
        by_severity=dict(by_severity),
        by_rule=dict(by_rule),
        items=items,
    )


def _money_anomalies(dataset: ProjectDataset) -> list[Anomaly]:
    items: list[Anomaly] = []

    for expense in dataset.expenditures:
        allocation = dataset.allocations_by_id.get(expense.allocation_id)
        if allocation:
            tranche = dataset.tranches_by_id.get(allocation.tranche_id)
            if tranche and tranche.actual_release is None:
                items.append(
                    Anomaly(
                        id=f"unreleased-{expense.expense_id}",
                        rule="spend_unreleased_tranche",
                        severity="high",
                        title="Spend from an unreleased tranche",
                        explanation=(
                            f"Expense {expense.expense_id} ({_inr(expense.amount_inr)}) was charged to "
                            f"allocation {allocation.allocation_id} on tranche {tranche.tranche_id}, "
                            "but that tranche has not been released yet."
                        ),
                        entity_type="expenditure",
                        entity_id=expense.expense_id,
                    )
                )

        if (
            expense.category in {"equipment", "civil_works"}
            and expense.amount_inr > PO_THRESHOLD
            and not expense.po_id
        ):
            items.append(
                Anomaly(
                    id=f"no-po-{expense.expense_id}",
                    rule="missing_purchase_order",
                    severity="high",
                    title="Large spend without a purchase order",
                    explanation=(
                        f"Expense {expense.expense_id} is {expense.category} for "
                        f"{_inr(expense.amount_inr)}, which is above ₹5,00,000, but has no purchase order."
                    ),
                    entity_type="expenditure",
                    entity_id=expense.expense_id,
                )
            )

        if (
            expense.requested_by
            and expense.approved_by
            and expense.requested_by == expense.approved_by
        ):
            items.append(
                Anomaly(
                    id=f"same-person-{expense.expense_id}",
                    rule="requester_equals_approver",
                    severity="high",
                    title="Same person requested and approved an expense",
                    explanation=(
                        f"Expense {expense.expense_id} was requested and approved by "
                        f"{expense.requested_by}. Requester and approver must be different people."
                    ),
                    entity_type="expenditure",
                    entity_id=expense.expense_id,
                )
            )

        for role, person_id in (
            ("requested", expense.requested_by),
            ("approved", expense.approved_by),
        ):
            if not person_id:
                continue
            person = dataset.researchers_by_id.get(person_id)
            if not person or person.status != "exited" or not person.left_on:
                continue
            # Only flag actions dated after the person left (or unparseable dates).
            if expense.expense_date is not None and expense.expense_date <= person.left_on:
                continue
            items.append(
                Anomaly(
                    id=f"exited-{role}-{expense.expense_id}",
                    rule="exited_person_expense",
                    severity="high",
                    title=f"Exited person {role} an expense",
                    explanation=(
                        f"{person.full_name} ({person_id}) left on {person.left_on}, "
                        f"but {role} expense {expense.expense_id} dated "
                        f"{expense.expense_date_raw or expense.expense_date}."
                    ),
                    entity_type="expenditure",
                    entity_id=expense.expense_id,
                )
            )

    for po_id, payments in dataset.expenditures_by_po.items():
        po = dataset.purchase_orders_by_id.get(po_id)
        if not po:
            continue
        paid = sum(p.amount_inr for p in payments)
        if paid > po.po_amount_inr + 0.01:
            items.append(
                Anomaly(
                    id=f"po-overpay-{po_id}",
                    rule="po_overpaid",
                    severity="high",
                    title="Purchase order payments exceed PO value",
                    explanation=(
                        f"{po_id} is valued at {_inr(po.po_amount_inr)}, but linked payments total "
                        f"{_inr(paid)} (over by {_inr(paid - po.po_amount_inr)})."
                    ),
                    entity_type="purchase_order",
                    entity_id=po_id,
                )
            )

    for po in dataset.purchase_orders:
        if (
            po.order_date
            and po.actual_delivery
            and po.actual_delivery < po.order_date
        ):
            items.append(
                Anomaly(
                    id=f"po-delivery-{po.po_id}",
                    rule="po_delivered_before_order",
                    severity="medium",
                    title="Delivery dated before the order",
                    explanation=(
                        f"{po.po_id} was ordered on {po.order_date} but shows actual delivery "
                        f"on {po.actual_delivery}."
                    ),
                    entity_type="purchase_order",
                    entity_id=po.po_id,
                )
            )

    return items


def _people_anomalies(dataset: ProjectDataset) -> list[Anomaly]:
    items: list[Anomaly] = []
    for sheet in dataset.timesheets:
        person = dataset.researchers_by_id.get(sheet.researcher_id)
        if not person or person.status != "exited" or not person.left_on:
            continue
        if sheet.week_start and sheet.week_start >= person.left_on:
            items.append(
                Anomaly(
                    id=f"exited-hours-{sheet.researcher_id}-{sheet.week_start_raw}",
                    rule="exited_person_timesheet",
                    severity="high",
                    title="Exited person logged hours",
                    explanation=(
                        f"{person.full_name} ({person.researcher_id}) left on {person.left_on} "
                        f"but logged {sheet.hours}h in week starting {sheet.week_start}."
                    ),
                    entity_type="timesheet",
                    entity_id=f"{sheet.researcher_id}:{sheet.week_start_raw}",
                )
            )
    return items


def _schedule_anomalies(dataset: ProjectDataset) -> list[Anomaly]:
    items: list[Anomaly] = []
    for dep in dataset.task_dependencies:
        pred = dataset.tasks_by_id.get(dep.predecessor_task_id)
        succ = dataset.tasks_by_id.get(dep.successor_task_id)
        if not pred or not succ:
            continue

        if (
            pred.actual_end
            and succ.actual_start
            and succ.actual_start < pred.actual_end
        ):
            items.append(
                Anomaly(
                    id=f"dep-start-{pred.task_id}-{succ.task_id}",
                    rule="task_dependency_order",
                    severity="high",
                    title="Successor started before predecessor finished",
                    explanation=(
                        f"{succ.task_id} ({succ.task_name}) started on {succ.actual_start}, "
                        f"but predecessor {pred.task_id} only finished on {pred.actual_end}."
                    ),
                    entity_type="task_dependency",
                    entity_id=f"{pred.task_id}->{succ.task_id}",
                )
            )
        elif succ.status == "completed" and pred.status != "completed":
            items.append(
                Anomaly(
                    id=f"dep-incomplete-{pred.task_id}-{succ.task_id}",
                    rule="task_dependency_order",
                    severity="high",
                    title="Successor completed while predecessor is incomplete",
                    explanation=(
                        f"{succ.task_id} is completed, but predecessor {pred.task_id} "
                        f"is still '{pred.status}'."
                    ),
                    entity_type="task_dependency",
                    entity_id=f"{pred.task_id}->{succ.task_id}",
                )
            )
    return items


def _component_anomalies(dataset: ProjectDataset) -> list[Anomaly]:
    items: list[Anomaly] = []
    for dep in dataset.component_dependencies:
        component = dataset.components_by_id.get(dep.component_id)
        needed = dataset.components_by_id.get(dep.depends_on_component_id)
        if not component or not needed:
            continue
        if COMPONENT_INSTALLED_RANK.get(component.status, 0) < 4:
            continue
        if COMPONENT_INSTALLED_RANK.get(needed.status, 0) < 4:
            items.append(
                Anomaly(
                    id=f"comp-dep-{component.component_id}-{needed.component_id}",
                    rule="component_dependency_install",
                    severity="high",
                    title="Component installed before a dependency was ready",
                    explanation=(
                        f"{component.component_id} ({component.component_name}) is '{component.status}', "
                        f"but it needs {needed.component_id} for {dep.dependency_type}, "
                        f"which is only '{needed.status}'."
                    ),
                    entity_type="component_dependency",
                    entity_id=f"{component.component_id}->{needed.component_id}",
                )
            )
    return items


def _milestone_anomalies(dataset: ProjectDataset) -> list[Anomaly]:
    items: list[Anomaly] = []
    today = dataset.as_of
    for milestone in dataset.milestones:
        linked = [
            dataset.tasks_by_id[task_id]
            for task_id in milestone.linked_task_ids
            if task_id in dataset.tasks_by_id
        ]
        incomplete = [t.task_id for t in linked if t.status != "completed"]
        if not incomplete:
            continue
        if milestone.reported_status == "achieved":
            items.append(
                Anomaly(
                    id=f"ms-achieved-{milestone.milestone_id}",
                    rule="milestone_self_report",
                    severity="medium",
                    title="Milestone reported achieved with incomplete tasks",
                    explanation=(
                        f"{milestone.milestone_id} is reported as achieved, but linked tasks still open: "
                        f"{', '.join(incomplete)}."
                    ),
                    entity_type="milestone",
                    entity_id=milestone.milestone_id,
                )
            )
        elif (
            milestone.reported_status == "on_track"
            and milestone.due_date
            and milestone.due_date < today
        ):
            items.append(
                Anomaly(
                    id=f"ms-late-{milestone.milestone_id}",
                    rule="milestone_self_report",
                    severity="medium",
                    title="Milestone still reported on track after its due date",
                    explanation=(
                        f"{milestone.milestone_id} was due {milestone.due_date} and still has open tasks "
                        f"({', '.join(incomplete)}), but reported status is on_track."
                    ),
                    entity_type="milestone",
                    entity_id=milestone.milestone_id,
                )
            )
    return items


def _timesheet_anomalies(dataset: ProjectDataset) -> list[Anomaly]:
    """Aggregate over-allocation into one finding per person."""
    week_hours: dict[tuple[str, date], float] = defaultdict(float)
    for sheet in dataset.timesheets:
        if sheet.week_start is None:
            continue
        week_hours[(sheet.researcher_id, sheet.week_start)] += sheet.hours

    over_by_person: dict[str, list[tuple[date, float, float]]] = defaultdict(list)
    for (researcher_id, week_start), hours in week_hours.items():
        person = dataset.researchers_by_id.get(researcher_id)
        if not person:
            continue
        cap = (person.project_allocation_pct / 100.0) * 40.0
        if hours > cap + 0.05:
            over_by_person[researcher_id].append((week_start, hours, cap))

    items: list[Anomaly] = []
    for researcher_id, weeks in over_by_person.items():
        person = dataset.researchers_by_id[researcher_id]
        weeks_sorted = sorted(weeks, key=lambda row: row[0])
        worst = max(weeks_sorted, key=lambda row: row[1] - row[2])
        items.append(
            Anomaly(
                id=f"over-alloc-{researcher_id}",
                rule="timesheet_over_allocation",
                severity="low",
                title="Hours logged above weekly allocation",
                explanation=(
                    f"{person.full_name} ({researcher_id}) is allocated "
                    f"{person.project_allocation_pct:.0f}% ({worst[2]:.1f}h/week) but exceeded that "
                    f"in {len(weeks_sorted)} week(s). Worst week {worst[0]} logged {worst[1]:.1f}h."
                ),
                entity_type="researcher",
                entity_id=researcher_id,
            )
        )
    return items


def _inr(amount: float) -> str:
    return f"₹{amount:,.0f}"
