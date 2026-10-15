import { useCallback, useState } from 'react'

import { StatusBadge } from '@/components/StatusBadge'
import { useDatasetQuery } from '@/hooks/useDatasetQuery'
import { getApiClient } from '@/lib/api'
import { formatCrore } from '@/lib/format'
import type { MilestoneDetail } from '@/interfaces/api'

export function ProgressPage() {
  const loader = useCallback(() => getApiClient().getProgress(), [])
  const { data, error, loading } = useDatasetQuery(loader)
  const [openId, setOpenId] = useState<string | null>('M4')

  return (
    <div className="space-y-8">
      <Header
        title="Milestones, tranches, and deadlines"
        subtitle="Computed status from linked tasks, plus funding-gate risk for each tranche."
      />
      {error && <ErrorBox message={error} />}
      {loading && !data && <p className="text-sm text-muted-foreground">Loading progress…</p>}

      {data && (
        <>
          <section className="space-y-3">
            <h2 className="text-sm font-semibold">Funding tranches</h2>
            <div className="grid gap-2 md:grid-cols-2">
              {data.tranches.map((t) => (
                <div key={t.tranche_id} className="rounded-lg border border-border/80 bg-card/70 px-3 py-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-sm font-medium">
                        {t.tranche_id} · {formatCrore(t.amount_inr)}
                      </p>
                      <p className="text-[11px] text-muted-foreground">
                        Condition: {t.condition_milestone_id}
                        {t.expected_release ? ` · expected ${t.expected_release}` : ''}
                        {t.days_to_expected != null ? ` (${t.days_to_expected}d)` : ''}
                      </p>
                    </div>
                    <StatusBadge value={t.risk} />
                  </div>
                  <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                    {t.risk_explanation}
                  </p>
                </div>
              ))}
            </div>
          </section>

          <section className="grid gap-6 lg:grid-cols-2">
            <DeadlineList title="Overdue" items={data.overdue_deadlines} empty="No overdue items" />
            <DeadlineList
              title="Upcoming (next 45 days for tasks)"
              items={data.upcoming_deadlines}
              empty="No upcoming deadlines"
            />
          </section>

          <section className="space-y-3">
            <h2 className="text-sm font-semibold">Milestone breakdown</h2>
            <div className="space-y-2">
              {data.milestones.map((m) => (
                <MilestoneCard
                  key={m.milestone_id}
                  milestone={m}
                  open={openId === m.milestone_id}
                  onToggle={() =>
                    setOpenId((prev) => (prev === m.milestone_id ? null : m.milestone_id))
                  }
                />
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  )
}

function MilestoneCard({
  milestone,
  open,
  onToggle,
}: {
  milestone: MilestoneDetail
  open: boolean
  onToggle: () => void
}) {
  return (
    <div className="rounded-lg border border-border/80 bg-card/70">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-start justify-between gap-3 px-3 py-3 text-left"
      >
        <div>
          <p className="text-sm font-medium">
            {milestone.milestone_id}: {milestone.milestone_name}
          </p>
          <p className="mt-0.5 text-[11px] text-muted-foreground">
            Due {milestone.due_date ?? 'n/a'}
            {milestone.days_to_due != null ? ` (${milestone.days_to_due}d)` : ''}
            {milestone.releases_tranche_id
              ? ` · releases ${milestone.releases_tranche_id}`
              : ' · no tranche'}
            {' · '}
            {milestone.linked_tasks_completed}/{milestone.linked_tasks_total} tasks done
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-1.5">
          <StatusBadge value={milestone.reported_status} />
          <StatusBadge value={milestone.computed_status} />
        </div>
      </button>
      {open && (
        <div className="space-y-2 border-t border-border/70 px-3 py-3">
          <p className="text-xs text-muted-foreground">{milestone.explanation}</p>
          {milestone.open_blocker_task_ids.length > 0 && (
            <p className="text-xs text-amber-800">
              Upstream blockers: {milestone.open_blocker_task_ids.join(', ')}
            </p>
          )}
          <div className="overflow-x-auto">
            <table className="w-full min-w-[28rem] text-left text-xs">
              <thead className="text-muted-foreground">
                <tr>
                  <th className="py-1 pr-2 font-medium">Task</th>
                  <th className="py-1 pr-2 font-medium">Dept</th>
                  <th className="py-1 pr-2 font-medium">Status</th>
                  <th className="py-1 pr-2 font-medium">Planned end</th>
                  <th className="py-1 font-medium">Waits on</th>
                </tr>
              </thead>
              <tbody>
                {milestone.linked_tasks.map((t) => (
                  <tr key={t.task_id} className="border-t border-border/40">
                    <td className="py-1.5 pr-2">
                      <span className="font-medium">{t.task_id}</span>
                      <span className="ml-1 text-muted-foreground">{t.task_name}</span>
                    </td>
                    <td className="py-1.5 pr-2">{t.dept_id}</td>
                    <td className="py-1.5 pr-2">
                      <StatusBadge value={t.status} />
                    </td>
                    <td className="py-1.5 pr-2">{t.planned_end ?? 'n/a'}</td>
                    <td className="py-1.5">
                      {t.open_predecessors.length
                        ? t.open_predecessors.join(', ')
                        : 'none open'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

function DeadlineList({
  title,
  items,
  empty,
}: {
  title: string
  items: { id: string; name: string; due_date: string; days_to_due: number; status: string; detail: string; kind: string }[]
  empty: string
}) {
  return (
    <div className="space-y-2">
      <h2 className="text-sm font-semibold">{title}</h2>
      {items.length === 0 ? (
        <p className="text-xs text-muted-foreground">{empty}</p>
      ) : (
        <div className="space-y-1.5">
          {items.map((item) => (
            <div
              key={`${item.kind}-${item.id}`}
              className="rounded-md border border-border/70 bg-card/60 px-3 py-2"
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs font-medium">
                  {item.id}: {item.name}
                </p>
                <StatusBadge value={item.status} />
              </div>
              <p className="mt-0.5 text-[11px] text-muted-foreground">
                {item.due_date} · {item.days_to_due}d · {item.detail}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function Header({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <section className="space-y-1">
      <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">{title}</h1>
      <p className="text-sm text-muted-foreground">{subtitle}</p>
    </section>
  )
}

function ErrorBox({ message }: { message: string }) {
  return (
    <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
      {message}
    </div>
  )
}
