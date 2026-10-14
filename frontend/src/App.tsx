import { Activity, ArrowRight, Waves } from 'lucide-react'
import { useEffect, useState } from 'react'

import { Button } from '@/components/ui/button'
import type { HealthStatus } from '@/interfaces/api'
import { getApiClient } from '@/lib/api'

export default function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    getApiClient()
      .getHealth()
      .then((status) => {
        if (!cancelled) {
          setHealth(status)
          setError(null)
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'API unreachable')
        }
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_oklch(0.94_0.03_210),_var(--background)_55%)]">
      <header className="border-b border-border/70 bg-background/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-2">
            <Waves className="h-4 w-4 text-primary" aria-hidden />
            <span className="text-sm font-semibold tracking-tight">Basin Watch</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Activity className="h-3.5 w-3.5" aria-hidden />
            {health ? (
              <span className="text-foreground">{health.status}</span>
            ) : error ? (
              <span className="text-red-700">offline</span>
            ) : (
              <span>checking…</span>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-5xl flex-col gap-8 px-4 py-12 sm:px-6 sm:py-16 md:py-20">
        <section className="max-w-2xl space-y-4">
          <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground">
            Project status console
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl md:text-5xl">
            Brahmaputra Basin Flood Early-Warning Network
          </h1>
          <p className="max-w-xl text-sm leading-relaxed text-muted-foreground sm:text-base">
            A read-only view of progress, funding, dependencies, people, and anomalies,
            built from the shared project CSVs. Assignment features land here next.
          </p>
          <div className="flex flex-wrap gap-2 pt-1">
            <Button size="sm">
              Open overview
              <ArrowRight className="h-3.5 w-3.5" aria-hidden />
            </Button>
            <Button size="sm" variant="outline">
              View docs
            </Button>
          </div>
        </section>

        <section className="grid gap-3 sm:grid-cols-2 md:grid-cols-3">
          {[
            ['Progress', 'Milestones, tranches, and overall readiness'],
            ['Money', 'Grant received vs allocated vs spent'],
            ['Attention', 'Rule breaks and blockers in plain language'],
          ].map(([title, body]) => (
            <div
              key={title}
              className="rounded-lg border border-border/80 bg-card/70 px-3.5 py-3 shadow-sm"
            >
              <h2 className="text-sm font-medium text-foreground">{title}</h2>
              <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{body}</p>
            </div>
          ))}
        </section>
      </main>
    </div>
  )
}
