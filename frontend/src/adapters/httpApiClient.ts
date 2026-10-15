import type {
  AnomaliesResponse,
  ApiClient,
  DependencyGraphResponse,
  HealthStatus,
  OverviewResponse,
  PeopleResponse,
  ProgressResponse,
  ReloadResponse,
} from '@/interfaces/api'

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    throw new Error(`Request failed (${response.status}) for ${path}`)
  }
  return (await response.json()) as T
}

export class HttpApiClient implements ApiClient {
  getHealth(): Promise<HealthStatus> {
    return requestJson('/api/health')
  }

  getOverview(): Promise<OverviewResponse> {
    return requestJson('/api/overview')
  }

  getProgress(): Promise<ProgressResponse> {
    return requestJson('/api/progress')
  }

  getAnomalies(): Promise<AnomaliesResponse> {
    return requestJson('/api/anomalies')
  }

  getTaskDependencies(): Promise<DependencyGraphResponse> {
    return requestJson('/api/dependencies/tasks')
  }

  getComponentDependencies(): Promise<DependencyGraphResponse> {
    return requestJson('/api/dependencies/components')
  }

  getPeople(): Promise<PeopleResponse> {
    return requestJson('/api/people')
  }

  refreshData(): Promise<ReloadResponse> {
    return requestJson('/api/data/refresh', { method: 'POST' })
  }
}
