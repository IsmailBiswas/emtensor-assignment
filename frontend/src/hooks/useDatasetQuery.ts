import { useEffect, useState } from 'react'

export function useDatasetQuery<T>(loader: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function run() {
      setLoading(true)
      try {
        const result = await loader()
        if (!cancelled) {
          setData(result)
          setError(null)
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void run()
    const onRefresh = () => {
      void run()
    }
    window.addEventListener('dataset-refreshed', onRefresh)
    return () => {
      cancelled = true
      window.removeEventListener('dataset-refreshed', onRefresh)
    }
  }, [loader])

  return { data, error, loading }
}
