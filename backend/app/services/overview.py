from app.domain.dataset import ProjectDataset
from app.api.schemas.overview import (
    DepartmentSummary,
    MilestoneSummary,
    OverviewResponse,
    TrancheSummary,
)


def build_overview(dataset: ProjectDataset) -> OverviewResponse:
    grant_total = sum(t.amount_inr for t in dataset.funding_tranches)
    grant_released = sum(
        t.amount_inr for t in dataset.funding_tranches if t.actual_release is not None
    )
    allocated = sum(a.amount_inr for a in dataset.budget_allocations)
    spent = sum(e.amount_inr for e in dataset.expenditures)
    people_active = sum(1 for r in dataset.researchers if r.status == "active")

    departments = [
        DepartmentSummary(
            dept_id=dept.dept_id,
            dept_name=dept.dept_name,
            total_budget_inr=dept.total_budget_inr,
            head_researcher_id=dept.head_researcher_id,
            staff_count=len(dataset.researchers_by_dept.get(dept.dept_id, [])),
            task_count=len(
                [
                    t
                    for t in dataset.tasks_by_dept.get(dept.dept_id, [])
                    if not t.is_work_package_root
                ]
            ),
        )
        for dept in dataset.departments
    ]

    milestones: list[MilestoneSummary] = []
    for milestone in dataset.milestones:
        linked = [
            dataset.tasks_by_id[task_id]
            for task_id in milestone.linked_task_ids
            if task_id in dataset.tasks_by_id
        ]
        completed = sum(1 for task in linked if task.status == "completed")
        milestones.append(
            MilestoneSummary(
                milestone_id=milestone.milestone_id,
                milestone_name=milestone.milestone_name,
                due_date=milestone.due_date,
                linked_task_ids=list(milestone.linked_task_ids),
                releases_tranche_id=milestone.releases_tranche_id,
                reported_status=milestone.reported_status,
                linked_tasks_completed=completed,
                linked_tasks_total=len(linked),
            )
        )

    tranches = [
        TrancheSummary(
            tranche_id=tranche.tranche_id,
            pct_of_grant=tranche.pct_of_grant,
            amount_inr=tranche.amount_inr,
            condition_milestone_id=tranche.condition_milestone_id,
            expected_release=tranche.expected_release,
            actual_release=tranche.actual_release,
            status=tranche.status,
        )
        for tranche in dataset.funding_tranches
    ]

    return OverviewResponse(
        as_of=dataset.as_of,
        grant_total_inr=grant_total,
        grant_released_inr=grant_released,
        allocated_inr=allocated,
        spent_inr=spent,
        people_active=people_active,
        people_total=len(dataset.researchers),
        departments=departments,
        milestones=milestones,
        tranches=tranches,
        counts=dataset.summary_counts(),
    )
