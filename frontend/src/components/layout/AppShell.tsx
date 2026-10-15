import {
  AlertTriangle,
  GitBranch,
  Landmark,
  LayoutDashboard,
  RefreshCw,
  Users,
  Waves,
} from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { getApiClient } from '@/lib/api'
import { cn } from '@/lib/utils'

const nav = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/progress', label: 'Milestones', icon: Landmark },
  { to: '/dependencies', label: 'Dependencies', icon: GitBranch },
  { to: '/anomalies', label: 'Anomalies', icon: AlertTriangle },
  { to: '/people', label: 'People', icon: Users },
]

export function AppShell() {
  const [refreshing, setRefreshing] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  async function handleRefresh() {
    setRefreshing(true)
    setMessage(null)
    try {
      await getApiClient().refreshData()
      setMessage('Data reloaded')
      window.dispatchEvent(new Event('dataset-refreshed'))
    } catch (err: unknown) {
      setMessage(err instanceof Error ? err.message : 'Refresh failed')
    } finally {
      setRefreshing(false)
    }
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_oklch(0.94_0.03_210),_var(--background)_55%)]">
      <header className="sticky top-0 z-20 border-b border-border/70 bg-background/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-3 sm:px-6">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Waves className="h-4 w-4 text-primary" aria-hidden />
              <span className="text-sm font-semibold tracking-tight">Basin Watch</span>
            </div>
            <div className="flex items-center gap-2">
              {message && (
                <span className="hidden text-[11px] text-muted-foreground sm:inline">{message}</span>
              )}
              <Button
                size="sm"
                variant="outline"
                onClick={() => void handleRefresh()}
                disabled={refreshing}
              >
                <RefreshCw
                  className={cn('h-3.5 w-3.5', refreshing && 'animate-spin')}
                  aria-hidden
                />
                Refresh
              </Button>
            </div>
          </div>
          <nav className="flex gap-1 overflow-x-auto pb-0.5">
            {nav.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  cn(
                    'inline-flex shrink-0 items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
                  )
                }
              >
                <Icon className="h-3.5 w-3.5" aria-hidden />
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
        <Outlet />
      </main>
    </div>
  )
}
