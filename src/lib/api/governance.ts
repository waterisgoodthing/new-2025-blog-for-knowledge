import { apiFetch } from './client'

export interface GovernanceSection {
  status: 'ready' | 'empty' | 'unavailable'
  source: string
  count: number | null
  detail: string | null
}

export interface GovernanceSummary {
  generated_at: string
  ai: GovernanceSection
  tasks: GovernanceSection
  statistics: GovernanceSection
  report: GovernanceSection
  settings: GovernanceSection
}

export function getGovernanceSummary(): Promise<GovernanceSummary> {
  return apiFetch<GovernanceSummary>('/api/admin/governance/summary')
}
