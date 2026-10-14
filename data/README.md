# Data dictionary

All amounts are in Indian Rupees (INR). All dates are ISO `YYYY-MM-DD` unless the data says otherwise, since it comes from
several offices. The "today" date for the project is **2026-09-15**. The `researchers.csv` file lists everyone on the
project: engineers, staff and faculty.

| File | One row is | Key columns |
|---|---|---|
| `departments.csv` | a department | `dept_id`, `total_budget_inr`, `head_researcher_id` → researchers |
| `researchers.csv` | a person on the project | `researcher_id`, `dept_id`, `role`, `project_allocation_pct`, `joined_on`, `left_on`, `status` (active / on_leave / exited) |
| `funding_tranches.csv` | a government release of funds | `tranche_id`, `amount_inr`, `condition_milestone_id` → milestones, `actual_release` (empty = not released) |
| `budget_allocations.csv` | money earmarked for a department and category from a tranche | `allocation_id`, `dept_id`, `category`, `tranche_id` |
| `work_packages.csv` | a task (work breakdown structure) | `task_id`, `parent_task_id` (WP-xxx = department work package), `component_id` → components, planned / actual dates, `status` |
| `task_dependencies.csv` | "successor cannot start until predecessor finishes" | `predecessor_task_id`, `successor_task_id`, `dependency_type`, `lag_days` |
| `milestones.csv` | a milestone the funding agency checks | `linked_task_ids` (semicolon-separated), `releases_tranche_id`, `reported_status` (self-reported) |
| `progress_updates.csv` | a progress report on a task | `task_id`, `report_date`, `percent_complete`, `blocker`, `note` |
| `components.csv` | a physical or software part of the system | `component_id`, `parent_component_id` (tree), `component_type`, `quantity`, `unit_cost_inr`, `governing_task_id` → tasks, `status` |
| `component_dependencies.csv` | "component needs another component to operate" | `component_id`, `depends_on_component_id`, `dependency_type` (enclosure / physical_space / platform / power / telemetry) |
| `purchase_orders.csv` | an order to a vendor | `po_id`, `component_id`, `po_amount_inr`, `order_date`, `actual_delivery`, `po_status` |
| `expenditures.csv` | a payment | `allocation_id` → allocations, `po_id` (optional), `amount_inr`, `invoice_no`, `requested_by`, `approved_by` |
| `timesheets.csv` | hours one person logged in one week | `researcher_id`, `week_start` (Monday), `task_id` (empty = general admin), `hours` |
| `component_hierarchy.json` | the component tree built from `components.csv` | convenience copy. If it disagrees with the CSV, the CSV wins |

Component types, from top to bottom: `system` → `subsystem` → `assembly` → `unit` → `sub_unit` → `part`.
Component statuses: `planned` → `ordered` → `delivered` → `in_progress` → `installed` → `tested`.
Task statuses: `not_started`, `in_progress`, `completed`.
Expense categories: `equipment`, `civil_works`, `consumables`, `manpower`, `travel`, `software_licences`, `contingency`.
