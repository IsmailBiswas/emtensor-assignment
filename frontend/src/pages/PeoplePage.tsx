import { useCallback, useMemo, useState } from 'react'

import { StatusBadge } from '@/components/StatusBadge'
import { useDatasetQuery } from '@/hooks/useDatasetQuery'
import { getApiClient } from '@/lib/api'

export function PeoplePage() {
  const loader = useCallback(() => getApiClient().getPeople(), [])
  const { data, error, loading } = useDatasetQuery(loader)
  const [query, setQuery] = useState('')
  const [dept, setDept] = useState('all')

  const departments = useMemo(() => {
    if (!data) return []
    return [...new Set(data.people.map((p) => p.dept_id))].sort()
  }, [data])

  const filtered = useMemo(() => {
    if (!data) return []
    const q = query.trim().toLowerCase()
    return data.people.filter((person) => {
      if (dept !== 'all' && person.dept_id !== dept) return false
      if (!q) return true
      return (
        person.full_name.toLowerCase().includes(q) ||
        person.researcher_id.toLowerCase().includes(q) ||
        person.role.toLowerCase().includes(q) ||
        person.email.toLowerCase().includes(q)
      )
    })
  }, [data, query, dept])

  return (
    <div className="space-y-6">
      <section className="space-y-1">
        <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">People</h1>
        <p className="text-sm text-muted-foreground">
          Everyone on the project from researchers.csv ({data?.total ?? '…'} people).
        </p>
      </section>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
        </div>
      )}
      {loading && !data && <p className="text-sm text-muted-foreground">Loading people…</p>}

      {data && (
        <>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search name, id, role…"
              className="h-8 w-full rounded-md border border-border bg-background px-2.5 text-xs outline-none ring-ring focus:ring-2 sm:max-w-xs"
            />
            <select
              value={dept}
              onChange={(e) => setDept(e.target.value)}
              className="h-8 rounded-md border border-border bg-background px-2 text-xs outline-none ring-ring focus:ring-2"
            >
              <option value="all">All departments</option>
              {departments.map((id) => (
                <option key={id} value={id}>
                  {id}
                </option>
              ))}
            </select>
          </div>

          <div className="overflow-x-auto rounded-lg border border-border/80 bg-card/70">
            <table className="w-full min-w-[40rem] text-left text-xs">
              <thead className="border-b border-border/80 text-muted-foreground">
                <tr>
                  <th className="px-3 py-2 font-medium">ID</th>
                  <th className="px-3 py-2 font-medium">Name</th>
                  <th className="px-3 py-2 font-medium">Dept</th>
                  <th className="px-3 py-2 font-medium">Role</th>
                  <th className="px-3 py-2 font-medium">Alloc %</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((person) => (
                  <tr key={person.researcher_id} className="border-b border-border/50 last:border-0">
                    <td className="px-3 py-2 font-medium">{person.researcher_id}</td>
                    <td className="px-3 py-2">
                      <div>{person.full_name}</div>
                      <div className="text-[11px] text-muted-foreground">{person.email}</div>
                    </td>
                    <td className="px-3 py-2">{person.dept_id}</td>
                    <td className="px-3 py-2">{person.role}</td>
                    <td className="px-3 py-2">{person.project_allocation_pct}</td>
                    <td className="px-3 py-2">
                      <StatusBadge value={person.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
