import { cn } from '@/lib/utils'

const tones: Record<string, string> = {
  high: 'bg-red-100 text-red-800',
  medium: 'bg-amber-100 text-amber-900',
  low: 'bg-sky-100 text-sky-900',
  released: 'bg-emerald-100 text-emerald-800',
  ready: 'bg-emerald-100 text-emerald-800',
  ok: 'bg-emerald-100 text-emerald-800',
  watch: 'bg-amber-100 text-amber-900',
  at_risk: 'bg-red-100 text-red-800',
  late: 'bg-red-100 text-red-800',
  complete: 'bg-emerald-100 text-emerald-800',
  completed: 'bg-emerald-100 text-emerald-800',
  due_soon: 'bg-amber-100 text-amber-900',
  in_progress: 'bg-sky-100 text-sky-900',
  on_track: 'bg-sky-100 text-sky-900',
  not_started: 'bg-secondary text-secondary-foreground',
  pending: 'bg-amber-100 text-amber-900',
  active: 'bg-emerald-100 text-emerald-800',
  exited: 'bg-red-100 text-red-800',
}

export function StatusBadge({ value }: { value: string }) {
  const key = value.toLowerCase()
  return (
    <span
      className={cn(
        'inline-flex rounded px-1.5 py-0.5 text-[11px] font-medium capitalize',
        tones[key] ?? 'bg-secondary text-secondary-foreground',
      )}
    >
      {value.replaceAll('_', ' ')}
    </span>
  )
}
