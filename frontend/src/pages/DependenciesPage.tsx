import { useCallback, useMemo, useState } from 'react'

import { StatusBadge } from '@/components/StatusBadge'
import { Button } from '@/components/ui/button'
import { useDatasetQuery } from '@/hooks/useDatasetQuery'
import type { DependencyGraphResponse, GraphNode } from '@/interfaces/api'
import { getApiClient } from '@/lib/api'
import { cn } from '@/lib/utils'

type GraphKind = 'tasks' | 'components'

export function DependenciesPage() {
  const [kind, setKind] = useState<GraphKind>('tasks')
  const [selected, setSelected] = useState<string | null>(null)

  const loader = useCallback(() => {
    const client = getApiClient()
    return kind === 'tasks'
      ? client.getTaskDependencies()
      : client.getComponentDependencies()
  }, [kind])

  const { data, error, loading } = useDatasetQuery(loader)

  const nodeMap = useMemo(() => {
    const map = new Map<string, GraphNode>()
    data?.nodes.forEach((n) => map.set(n.id, n))
    return map
  }, [data])

  const selectedNode = selected ? nodeMap.get(selected) : null
  const incoming = data?.edges.filter((e) => e.target === selected) ?? []
  const outgoing = data?.edges.filter((e) => e.source === selected) ?? []

  return (
    <div className="space-y-6">
      <section className="space-y-1">
        <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">Dependencies</h1>
        <p className="text-sm text-muted-foreground">
          Read left to right: earlier columns must finish before later ones can proceed.
          Tap a card to see what it waits on and what it blocks.
        </p>
      </section>

      <div className="flex flex-wrap gap-1.5">
        <Button
          size="sm"
          variant={kind === 'tasks' ? 'default' : 'outline'}
          onClick={() => {
            setKind('tasks')
            setSelected(null)
          }}
        >
          Task graph
        </Button>
        <Button
          size="sm"
          variant={kind === 'components' ? 'default' : 'outline'}
          onClick={() => {
            setKind('components')
            setSelected(null)
          }}
        >
          Component graph
        </Button>
      </div>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
        </div>
      )}
      {loading && !data && <p className="text-sm text-muted-foreground">Loading graph…</p>}

      {data && (
        <div className="grid gap-4 lg:grid-cols-[1fr_16rem]">
          <DependencyBoard
            data={data}
            selected={selected}
            onSelect={setSelected}
          />
          <aside className="rounded-lg border border-border/80 bg-card/70 p-3">
            {selectedNode ? (
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium">{selectedNode.id}</p>
                  <p className="text-xs text-muted-foreground">{selectedNode.label}</p>
                </div>
                <StatusBadge value={selectedNode.status} />
                <p className="text-[11px] text-muted-foreground">{selectedNode.detail}</p>
                <div>
                  <p className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                    Waits on
                  </p>
                  <EdgeList
                    edges={incoming}
                    pick={(e) => e.source}
                    empty="Nothing upstream"
                    nodeMap={nodeMap}
                    onSelect={setSelected}
                  />
                </div>
                <div>
                  <p className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                    Blocks
                  </p>
                  <EdgeList
                    edges={outgoing}
                    pick={(e) => e.target}
                    empty="Nothing downstream"
                    nodeMap={nodeMap}
                    onSelect={setSelected}
                  />
                </div>
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">
                Select a {kind === 'tasks' ? 'task' : 'component'} to inspect its chain.
              </p>
            )}
          </aside>
        </div>
      )}
    </div>
  )
}

function DependencyBoard({
  data,
  selected,
  onSelect,
}: {
  data: DependencyGraphResponse
  selected: string | null
  onSelect: (id: string) => void
}) {
  return (
    <div className="overflow-x-auto rounded-lg border border-border/80 bg-card/40 p-3">
      <div className="flex min-w-max gap-3">
        {data.levels.map((levelIds, levelIdx) => (
          <div key={levelIdx} className="w-52 shrink-0 space-y-2">
            <p className="px-1 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
              Step {levelIdx + 1}
            </p>
            {levelIds.map((id) => {
              const node = data.nodes.find((n) => n.id === id)
              if (!node) return null
              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => onSelect(id)}
                  className={cn(
                    'w-full rounded-md border px-2.5 py-2 text-left transition-colors',
                    selected === id
                      ? 'border-primary bg-primary/5'
                      : 'border-border/80 bg-card/80 hover:border-primary/40',
                  )}
                >
                  <div className="flex items-start justify-between gap-1">
                    <p className="text-xs font-medium">{node.id}</p>
                    <span className="text-[10px] text-muted-foreground">{node.group}</span>
                  </div>
                  <p className="mt-0.5 line-clamp-2 text-[11px] text-muted-foreground">
                    {node.label}
                  </p>
                  <div className="mt-1.5">
                    <StatusBadge value={node.status} />
                  </div>
                </button>
              )
            })}
          </div>
        ))}
      </div>
      <p className="mt-3 text-[11px] text-muted-foreground">
        {data.nodes.length} nodes · {data.edges.length} links · scroll sideways on smaller screens
      </p>
    </div>
  )
}

function EdgeList({
  edges,
  pick,
  empty,
  nodeMap,
  onSelect,
}: {
  edges: { source: string; target: string; label: string }[]
  pick: (edge: { source: string; target: string }) => string
  empty: string
  nodeMap: Map<string, GraphNode>
  onSelect: (id: string) => void
}) {
  if (edges.length === 0) {
    return <p className="mt-1 text-xs text-muted-foreground">{empty}</p>
  }
  return (
    <ul className="mt-1 space-y-1">
      {edges.map((edge) => {
        const id = pick(edge)
        const node = nodeMap.get(id)
        return (
          <li key={`${edge.source}-${edge.target}`}>
            <button
              type="button"
              className="text-left text-xs text-primary hover:underline"
              onClick={() => onSelect(id)}
            >
              {id}
              {node ? ` · ${node.label}` : ''}
            </button>
            <p className="text-[10px] text-muted-foreground">{edge.label}</p>
          </li>
        )
      })}
    </ul>
  )
}
