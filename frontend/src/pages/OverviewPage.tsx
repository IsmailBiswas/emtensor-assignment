import { Landmark, Users } from 'lucide-react'
import { useCallback, type ReactNode } from 'react'
import { Link } from 'react-router-dom'

import { StatusBadge } from '@/components/StatusBadge'
import { Button } from '@/components/ui/button'
import { useDatasetQuery } from '@/hooks/useDatasetQuery'
import { getApiClient } from '@/lib/api'
import { formatCrore, formatInr } from '@/lib/format'

export function OverviewPage() {
  const loader = useCallback(() => getApiClient().getOverview(), [])
  const anomaliesLoader = useCallback(() => getApiClient().getAnomalies(), [])
  const { data, error, loading } = useDatasetQuery(loader)
  const anomalies = useDatasetQuery(anomaliesLoader)

  return (
    <div className="space-y-8">
      <section className="max-w-3xl space-y-2">
        <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground">
          Project status
        </p>
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
          Brahmaputra Basin Flood Early-Warning Network
        </h1>
        <p className="text-sm text-muted-foreground">
          Funding, departments, and attention items from the loaded CSV snapshot
          {data ? ` (as of ${data.as_of})` : ''}.
        </p>
      </section>

      {error && <ErrorBox message={error} />}
      {loading && !data && <p className="text-sm text-muted-foreground">Loading overview…</p>}

      {data && (
        <>
          <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              icon={<Landmark className="h-3.5 w-3.5" aria-hidden />}
              label="Grant released"
              value={formatCrore(data.grant_released_inr)}
              hint={`of ${formatCrore(data.grant_total_inr)} total`}
            />
            <StatCard label="Allocated" value={formatCrore(data.allocated_inr)} hint="Budget earmarked" />
            <StatCard label="Spent" value={formatCrore(data.spent_inr)} hint="From expenditures" />
            <StatCard
              icon={<Users className="h-3.5 w-3.5" aria-hidden />}
              label="People"
              value={`${data.people_active}/${data.people_total}`}
              hint="Active / total"
            />
          </section>

          {anomalies.data && (
            <section className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-amber-200 bg-amber-50 px-3.5 py-3">
              <div>
                <p className="text-sm font-medium text-amber-950">
                  {anomalies.data.total} anomalies need attention
                </p>
                <p className="text-xs text-amber-900/80">
                  High: {anomalies.data.by_severity.high ?? 0} · Medium:{' '}
                  {anomalies.data.by_severity.medium ?? 0} · Low:{' '}
                  {anomalies.data.by_severity.low ?? 0}
                </p>
              </div>
              <Button asChild size="sm" variant="outline">
                <Link to="/anomalies">View anomalies</Link>
              </Button>
            </section>
          )}

          <section className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold">Tranches</h2>
                <Link to="/progress" className="text-xs text-primary hover:underline">
                  Full breakdown
                </Link>
              </div>
              <SimpleTable
                headers={['Tranche', 'Amount', 'Status']}
                rows={data.tranches.map((t) => [
                  t.tranche_id,
                  formatCrore(t.amount_inr),
                  <StatusBadge key={t.tranche_id} value={t.status} />,
                ])}
              />
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold">Milestones</h2>
                <Link to="/progress" className="text-xs text-primary hover:underline">
                  Details
                </Link>
              </div>
              <div className="space-y-2">
                {data.milestones.map((m) => (
                  <div key={m.milestone_id} className="rounded-lg border border-border/80 bg-card/70 px-3 py-2.5">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-xs font-medium">
                        {m.milestone_id}: {m.milestone_name}
                      </p>
                      <StatusBadge value={m.reported_status} />
                    </div>
                    <p className="mt-1 text-[11px] text-muted-foreground">
                      Due {m.due_date ?? 'n/a'} · tasks {m.linked_tasks_completed}/
                      {m.linked_tasks_total}
                      {m.releases_tranche_id ? ` · releases ${m.releases_tranche_id}` : ''}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="space-y-3">
            <h2 className="text-sm font-semibold">Departments</h2>
            <SimpleTable
              headers={['Dept', 'Budget', 'Staff', 'Tasks', 'Head']}
              rows={data.departments.map((d) => [
                <span key={d.dept_id}>
                  <span className="font-medium">{d.dept_id}</span>
                  <span className="ml-1.5 text-muted-foreground">{d.dept_name}</span>
                </span>,
                formatInr(d.total_budget_inr),
                String(d.staff_count),
                String(d.task_count),
                d.head_researcher_id,
              ])}
            />
          </section>
        </>
      )}
    </div>
  )
}

function StatCard({
  label,
  value,
  hint,
  icon,
}: {
  label: string
  value: string
  hint: string
  icon?: ReactNode
}) {
  return (
    <div className="rounded-lg border border-border/80 bg-card/70 px-3.5 py-3 shadow-sm">
      <div className="flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
        {icon}
        {label}
      </div>
      <p className="mt-1 text-lg font-semibold tracking-tight">{value}</p>
      <p className="text-[11px] text-muted-foreground">{hint}</p>
    </div>
  )
}

function SimpleTable({
  headers,
  rows,
}: {
  headers: string[]
  rows: ReactNode[][]
}) {
  return (
    <div className="overflow-x-auto rounded-lg border border-border/80 bg-card/70">
      <table className="w-full min-w-[24rem] text-left text-xs">
        <thead className="border-b border-border/80 text-muted-foreground">
          <tr>
            {headers.map((h) => (
              <th key={h} className="px-3 py-2 font-medium">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx} className="border-b border-border/50 last:border-0">
              {row.map((cell, cidx) => (
                <td key={cidx} className="px-3 py-2 align-top">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function ErrorBox({ message }: { message: string }) {
  return (
    <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
      {message}
    </div>
  )
}
