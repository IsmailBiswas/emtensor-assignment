import { useCallback, useMemo, useState } from 'react'

import { StatusBadge } from '@/components/StatusBadge'
import { Button } from '@/components/ui/button'
import { useDatasetQuery } from '@/hooks/useDatasetQuery'
import { getApiClient } from '@/lib/api'

export function AnomaliesPage() {
  const loader = useCallback(() => getApiClient().getAnomalies(), [])
  const { data, error, loading } = useDatasetQuery(loader)
  const [severity, setSeverity] = useState<string>('all')
  const [rule, setRule] = useState<string>('all')

  const rules = useMemo(
    () => (data ? Object.keys(data.by_rule).sort() : []),
    [data],
  )

  const filtered = useMemo(() => {
    if (!data) return []
    return data.items.filter((item) => {
      if (severity !== 'all' && item.severity !== severity) return false
      if (rule !== 'all' && item.rule !== rule) return false
      return true
    })
  }, [data, severity, rule])

  return (
    <div className="space-y-6">
      <section className="space-y-1">
        <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">Anomalies</h1>
        <p className="text-sm text-muted-foreground">
          Records that break project rules or look suspicious, explained in plain language.
        </p>
      </section>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
        </div>
      )}
      {loading && !data && <p className="text-sm text-muted-foreground">Scanning data…</p>}

      {data && (
        <>
          <div className="flex flex-wrap gap-2 text-xs">
            <SummaryChip label="Total" value={String(data.total)} />
            <SummaryChip label="High" value={String(data.by_severity.high ?? 0)} />
            <SummaryChip label="Medium" value={String(data.by_severity.medium ?? 0)} />
            <SummaryChip label="Low" value={String(data.by_severity.low ?? 0)} />
          </div>

          <div className="flex flex-wrap gap-1.5">
            {['all', 'high', 'medium', 'low'].map((value) => (
              <Button
                key={value}
                size="sm"
                variant={severity === value ? 'default' : 'outline'}
                onClick={() => setSeverity(value)}
              >
                {value}
              </Button>
            ))}
          </div>

          <div className="flex flex-wrap gap-1.5">
            <Button
              size="sm"
              variant={rule === 'all' ? 'default' : 'outline'}
              onClick={() => setRule('all')}
            >
              all rules
            </Button>
            {rules.map((value) => (
              <Button
                key={value}
                size="sm"
                variant={rule === value ? 'default' : 'outline'}
                onClick={() => setRule(value)}
              >
                {value.replaceAll('_', ' ')}
              </Button>
            ))}
          </div>

          <p className="text-xs text-muted-foreground">
            Showing {filtered.length} of {data.total}
          </p>

          <div className="space-y-2">
            {filtered.map((item) => (
              <article
                key={item.id}
                className="rounded-lg border border-border/80 bg-card/70 px-3 py-3"
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="text-sm font-medium">{item.title}</p>
                    <p className="mt-0.5 text-[11px] text-muted-foreground">
                      {item.entity_type} · {item.entity_id} · {item.rule.replaceAll('_', ' ')}
                    </p>
                  </div>
                  <StatusBadge value={item.severity} />
                </div>
                <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                  {item.explanation}
                </p>
              </article>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

function SummaryChip({ label, value }: { label: string; value: string }) {
  return (
    <span className="rounded-md border border-border/80 bg-card/70 px-2.5 py-1">
      <span className="text-muted-foreground">{label}: </span>
      <span className="font-medium">{value}</span>
    </span>
  )
}
