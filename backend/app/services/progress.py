from __future__ import annotations

from datetime import date

from app.api.schemas.progress import (
    DeadlineItem,
    LinkedTaskStatus,
    MilestoneDetail,
    ProgressResponse,
    TrancheDetail,
)
from app.domain.dataset import ProjectDataset


def build_progress(dataset: ProjectDataset) -> ProgressResponse:
    today = dataset.as_of
    milestones = [_milestone_detail(dataset, milestone.milestone_id) for milestone in dataset.milestones]
    milestone_by_id = {m.milestone_id: m for m in milestones}
    tranches = [
        _tranche_detail(dataset, tranche.tranche_id, milestone_by_id)
        for tranche in dataset.funding_tranches
    ]

    upcoming: list[DeadlineItem] = []
    overdue: list[DeadlineItem] = []

    for milestone in milestones:
        if not milestone.due_date:
            continue
        item = DeadlineItem(
            kind="milestone",
            id=milestone.milestone_id,
            name=milestone.milestone_name,
            due_date=milestone.due_date,
            days_to_due=(milestone.due_date - today).days,
            status=milestone.computed_status,
            detail=(
                f"{milestone.linked_tasks_completed}/{milestone.linked_tasks_total} linked tasks done"
            ),
        )
        if item.days_to_due < 0 and milestone.linked_tasks_completed < milestone.linked_tasks_total:
            overdue.append(item)
        elif item.days_to_due >= 0:
            upcoming.append(item)

    for task in dataset.work_packages:
        if task.is_work_package_root or not task.planned_end:
            continue
        if task.status == "completed":
            continue
        days = (task.planned_end - today).days
        item = DeadlineItem(
            kind="task",
            id=task.task_id,
            name=task.task_name,
            due_date=task.planned_end,
            days_to_due=days,
            status=task.status,
            detail=f"{task.dept_id} · {task.status}",
        )
        if days < 0:
            overdue.append(item)
        elif days <= 45:
            upcoming.append(item)

    upcoming.sort(key=lambda d: d.days_to_due)
    overdue.sort(key=lambda d: d.days_to_due)

    return ProgressResponse(
        as_of=today,
        milestones=milestones,
        tranches=tranches,
        upcoming_deadlines=upcoming[:20],
        overdue_deadlines=overdue[:20],
    )


def _milestone_detail(dataset: ProjectDataset, milestone_id: str) -> MilestoneDetail:
    milestone = dataset.milestones_by_id[milestone_id]
    today = dataset.as_of
    linked: list[LinkedTaskStatus] = []
    open_blockers: list[str] = []

    for task_id in milestone.linked_task_ids:
        task = dataset.tasks_by_id.get(task_id)
        if not task:
            continue
        open_preds = [
            pred_id
            for pred_id in dataset.task_predecessors.get(task_id, [])
            if dataset.tasks_by_id.get(pred_id)
            and dataset.tasks_by_id[pred_id].status != "completed"
        ]
        open_blockers.extend(open_preds)
        linked.append(
            LinkedTaskStatus(
                task_id=task.task_id,
                task_name=task.task_name,
                dept_id=task.dept_id,
                status=task.status,
                planned_end=task.planned_end,
                actual_end=task.actual_end,
                blocker_count=len(open_preds),
                open_predecessors=open_preds,
            )
        )

    completed = sum(1 for task in linked if task.status == "completed")
    total = len(linked)
    computed = _compute_milestone_status(milestone.due_date, today, completed, total)
    explanation = _milestone_explanation(milestone.reported_status, computed, completed, total)

    days_to_due = None
    if milestone.due_date:
        days_to_due = (milestone.due_date - today).days

    return MilestoneDetail(
        milestone_id=milestone.milestone_id,
        milestone_name=milestone.milestone_name,
        due_date=milestone.due_date,
        days_to_due=days_to_due,
        reported_status=milestone.reported_status,
        computed_status=computed,
        releases_tranche_id=milestone.releases_tranche_id,
        linked_tasks=linked,
        linked_tasks_completed=completed,
        linked_tasks_total=total,
        open_blocker_task_ids=sorted(set(open_blockers)),
        explanation=explanation,
    )


def _tranche_detail(
    dataset: ProjectDataset,
    tranche_id: str,
    milestones: dict[str, MilestoneDetail],
) -> TrancheDetail:
    tranche = dataset.tranches_by_id[tranche_id]
    today = dataset.as_of
    days_to_expected = None
    if tranche.expected_release:
        days_to_expected = (tranche.expected_release - today).days

    milestone = milestones.get(tranche.condition_milestone_id)
    risk = "ok"
    explanation = f"Conditioned on {tranche.condition_milestone_id}."

    if tranche.actual_release is not None:
        risk = "released"
        explanation = f"Released on {tranche.actual_release}."
    elif milestone:
        incomplete = milestone.linked_tasks_total - milestone.linked_tasks_completed
        has_blockers = bool(milestone.open_blocker_task_ids)
        if incomplete == 0:
            risk = "ready"
            explanation = (
                f"Condition milestone {milestone.milestone_id} linked tasks are complete; "
                "awaiting release."
            )
        elif milestone.due_date and milestone.due_date < today:
            risk = "at_risk"
            explanation = (
                f"Condition milestone {milestone.milestone_id} is past due with "
                f"{incomplete} open linked task(s)"
                + (f" and upstream blockers {', '.join(milestone.open_blocker_task_ids)}." if has_blockers else ".")
            )
        elif has_blockers or incomplete > 0:
            days = milestone.days_to_due if milestone.days_to_due is not None else 999
            risk = "at_risk" if days <= 30 else "watch"
            explanation = (
                f"Condition milestone {milestone.milestone_id} still has {incomplete} open task(s)"
                + (f"; blocked by {', '.join(milestone.open_blocker_task_ids)}" if has_blockers else "")
                + f". Due in {days} day(s)."
            )

    return TrancheDetail(
        tranche_id=tranche.tranche_id,
        pct_of_grant=tranche.pct_of_grant,
        amount_inr=tranche.amount_inr,
        status=tranche.status,
        condition_milestone_id=tranche.condition_milestone_id,
        expected_release=tranche.expected_release,
        actual_release=tranche.actual_release,
        days_to_expected=days_to_expected,
        risk=risk,
        risk_explanation=explanation,
    )


def _compute_milestone_status(
    due_date: date | None,
    today: date,
    completed: int,
    total: int,
) -> str:
    if total == 0:
        return "unknown"
    if completed == total:
        return "complete"
    if due_date and due_date < today:
        return "late"
    if due_date and (due_date - today).days <= 30:
        return "due_soon"
    return "in_progress"


def _milestone_explanation(
    reported: str,
    computed: str,
    completed: int,
    total: int,
) -> str:
    base = f"{completed}/{total} linked tasks completed. Reported '{reported}', computed '{computed}'."
    if reported != computed and not (
        reported == "on_track" and computed in {"in_progress", "due_soon"}
    ):
        return base + " Self-reported status may not match task reality."
    return base
