from __future__ import annotations

from collections import defaultdict, deque

from app.api.schemas.dependencies import (
    DependencyGraphResponse,
    GraphEdge,
    GraphNode,
    PeoplePerson,
    PeopleResponse,
)
from app.domain.dataset import ProjectDataset


def build_task_dependency_graph(dataset: ProjectDataset) -> DependencyGraphResponse:
    """Graph of tasks that participate in at least one dependency edge."""
    involved: set[str] = set()
    edges: list[GraphEdge] = []
    for dep in dataset.task_dependencies:
        if dep.predecessor_task_id not in dataset.tasks_by_id:
            continue
        if dep.successor_task_id not in dataset.tasks_by_id:
            continue
        involved.add(dep.predecessor_task_id)
        involved.add(dep.successor_task_id)
        edges.append(
            GraphEdge(
                source=dep.predecessor_task_id,
                target=dep.successor_task_id,
                kind=dep.dependency_type or "finish_to_start",
                label="must finish before",
            )
        )

    levels_map = _topo_levels(involved, dataset.task_successors)
    nodes = [
        GraphNode(
            id=task_id,
            label=dataset.tasks_by_id[task_id].task_name,
            group=dataset.tasks_by_id[task_id].dept_id,
            status=dataset.tasks_by_id[task_id].status or "unknown",
            detail=_task_detail(dataset, task_id),
            level=levels_map.get(task_id, 0),
        )
        for task_id in sorted(involved)
    ]

    level_buckets: dict[int, list[str]] = defaultdict(list)
    for node in nodes:
        level_buckets[node.level].append(node.id)
    levels = [level_buckets[i] for i in sorted(level_buckets)]

    return DependencyGraphResponse(nodes=nodes, edges=edges, levels=levels)


def build_component_dependency_graph(dataset: ProjectDataset) -> DependencyGraphResponse:
    involved: set[str] = set()
    edges: list[GraphEdge] = []
    for dep in dataset.component_dependencies:
        if dep.component_id not in dataset.components_by_id:
            continue
        if dep.depends_on_component_id not in dataset.components_by_id:
            continue
        involved.add(dep.component_id)
        involved.add(dep.depends_on_component_id)
        # Edge direction: dependency must be ready before component (needed -> component)
        edges.append(
            GraphEdge(
                source=dep.depends_on_component_id,
                target=dep.component_id,
                kind=dep.dependency_type,
                label=f"provides {dep.dependency_type}",
            )
        )

    successors: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        successors[edge.source].append(edge.target)

    levels_map = _topo_levels(involved, dict(successors))
    nodes = [
        GraphNode(
            id=component_id,
            label=dataset.components_by_id[component_id].component_name,
            group=dataset.components_by_id[component_id].owner_dept_id or "n/a",
            status=dataset.components_by_id[component_id].status,
            detail=(
                f"{dataset.components_by_id[component_id].component_type} · "
                f"{dataset.components_by_id[component_id].status}"
            ),
            level=levels_map.get(component_id, 0),
        )
        for component_id in sorted(involved)
    ]

    level_buckets: dict[int, list[str]] = defaultdict(list)
    for node in nodes:
        level_buckets[node.level].append(node.id)
    levels = [level_buckets[i] for i in sorted(level_buckets)]

    return DependencyGraphResponse(nodes=nodes, edges=edges, levels=levels)


def build_people(dataset: ProjectDataset) -> PeopleResponse:
    people = [
        PeoplePerson(
            researcher_id=person.researcher_id,
            full_name=person.full_name,
            dept_id=person.dept_id,
            role=person.role,
            status=person.status,
            project_allocation_pct=person.project_allocation_pct,
            email=person.email,
        )
        for person in dataset.researchers
    ]
    people.sort(key=lambda p: (p.dept_id, p.full_name))
    return PeopleResponse(total=len(people), people=people)


def _task_detail(dataset: ProjectDataset, task_id: str) -> str:
    task = dataset.tasks_by_id[task_id]
    preds = dataset.task_predecessors.get(task_id, [])
    succs = dataset.task_successors.get(task_id, [])
    bits = [f"{task.dept_id}", task.status or "n/a"]
    if preds:
        bits.append(f"waits on {len(preds)}")
    if succs:
        bits.append(f"blocks {len(succs)}")
    if task.planned_end:
        bits.append(f"planned end {task.planned_end}")
    return " · ".join(bits)


def _topo_levels(nodes: set[str], successors: dict[str, list[str]]) -> dict[str, int]:
    indegree = {node: 0 for node in nodes}
    for source, targets in successors.items():
        if source not in nodes:
            continue
        for target in targets:
            if target in indegree:
                indegree[target] += 1

    queue: deque[str] = deque(sorted(node for node, deg in indegree.items() if deg == 0))
    levels = {node: 0 for node in queue}
    seen = 0

    while queue:
        node = queue.popleft()
        seen += 1
        for nxt in successors.get(node, []):
            if nxt not in indegree:
                continue
            indegree[nxt] -= 1
            levels[nxt] = max(levels.get(nxt, 0), levels[node] + 1)
            if indegree[nxt] == 0:
                queue.append(nxt)

    # Cycles or leftovers: pin remaining nodes
    for node in nodes:
        levels.setdefault(node, 0)
    return levels
