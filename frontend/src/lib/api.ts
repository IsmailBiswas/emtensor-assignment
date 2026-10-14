import { HttpApiClient } from '@/adapters/httpApiClient'
import type { ApiClient } from '@/interfaces/api'

let client: ApiClient | null = null

export function getApiClient(): ApiClient {
  if (!client) {
    client = new HttpApiClient()
  }
  return client
}
