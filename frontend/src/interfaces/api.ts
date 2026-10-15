export interface HealthStatus {
  status: string
  service: string
}

export interface DatasetSummary {
  as_of: string
  loaded_at: string
  counts: Record<string, number>
}

export interface ReloadResponse {
  status: string
  summary: DatasetSummary
}

export interface DepartmentSummary {
  dept_id: string
  dept_name: string
  total_budget_inr: number
  head_researcher_id: string
  staff_count: number
  task_count: number
}

export interface MilestoneSummary {
  milestone_id: string
  milestone_name: string
  due_date: string | null
  linked_task_ids: string[]
  releases_tranche_id: string | null
  reported_status: string
  linked_tasks_completed: number
  linked_tasks_total: number
}

export interface TrancheSummary {
  tranche_id: string
  pct_of_grant: number
  amount_inr: number
  condition_milestone_id: string
  expected_release: string | null
  actual_release: string | null
  status: string
}

export interface OverviewResponse {
  as_of: string
  grant_total_inr: number
  grant_released_inr: number
  allocated_inr: number
  spent_inr: number
  people_active: number
  people_total: number
  departments: DepartmentSummary[]
  milestones: MilestoneSummary[]
  tranches: TrancheSummary[]
  counts: Record<string, number>
}

export interface LinkedTaskStatus {
  task_id: string
  task_name: string
  dept_id: string
  status: string
  planned_end: string | null
  actual_end: string | null
  blocker_count: number
  open_predecessors: string[]
}

export interface MilestoneDetail {
  milestone_id: string
  milestone_name: string
  due_date: string | null
  days_to_due: number | null
  reported_status: string
  computed_status: string
  releases_tranche_id: string | null
  linked_tasks: LinkedTaskStatus[]
  linked_tasks_completed: number
  linked_tasks_total: number
  open_blocker_task_ids: string[]
  explanation: string
}

export interface TrancheDetail {
  tranche_id: string
  pct_of_grant: number
  amount_inr: number
  status: string
  condition_milestone_id: string
  expected_release: string | null
  actual_release: string | null
  days_to_expected: number | null
  risk: string
  risk_explanation: string
}

export interface DeadlineItem {
  kind: string
  id: string
  name: string
  due_date: string
  days_to_due: number
  status: string
  detail: string
}

export interface ProgressResponse {
  as_of: string
  milestones: MilestoneDetail[]
  tranches: TrancheDetail[]
  upcoming_deadlines: DeadlineItem[]
  overdue_deadlines: DeadlineItem[]
}

export interface Anomaly {
  id: string
  rule: string
  severity: string
  title: string
  explanation: string
  entity_type: string
  entity_id: string
}

export interface AnomaliesResponse {
  as_of: string
  total: number
  by_severity: Record<string, number>
  by_rule: Record<string, number>
  items: Anomaly[]
}

export interface GraphNode {
  id: string
  label: string
  group: string
  status: string
  detail: string
  level: number
}

export interface GraphEdge {
  source: string
  target: string
  kind: string
  label: string
}

export interface DependencyGraphResponse {
  nodes: GraphNode[]
  edges: GraphEdge[]
  levels: string[][]
}

export interface PeoplePerson {
  researcher_id: string
  full_name: string
  dept_id: string
  role: string
  status: string
  project_allocation_pct: number
  email: string
}

export interface PeopleResponse {
  total: number
  people: PeoplePerson[]
}

export interface ApiClient {
  getHealth(): Promise<HealthStatus>
  getOverview(): Promise<OverviewResponse>
  getProgress(): Promise<ProgressResponse>
  getAnomalies(): Promise<AnomaliesResponse>
  getTaskDependencies(): Promise<DependencyGraphResponse>
  getComponentDependencies(): Promise<DependencyGraphResponse>
  getPeople(): Promise<PeopleResponse>
  refreshData(): Promise<ReloadResponse>
}
