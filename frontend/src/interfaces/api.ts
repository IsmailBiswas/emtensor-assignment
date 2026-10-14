export interface HealthStatus {
  status: string
  service: string
}

export interface ApiClient {
  getHealth(): Promise<HealthStatus>
}
