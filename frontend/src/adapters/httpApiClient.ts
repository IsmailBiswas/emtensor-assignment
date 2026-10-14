import type { ApiClient, HealthStatus } from '@/interfaces/api'

const API_BASE = import.meta.env.VITE_API_BASE ?? ''

export class HttpApiClient implements ApiClient {
  async getHealth(): Promise<HealthStatus> {
    const response = await fetch(`${API_BASE}/api/health`)
    if (!response.ok) {
      throw new Error(`Health check failed (${response.status})`)
    }
    return (await response.json()) as HealthStatus
  }
}
