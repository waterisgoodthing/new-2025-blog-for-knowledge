import { apiFetch } from './client'

export interface KpAnalytics {
  knowledge_point_id: number
  attempt_count: number
  wrong_count: number
  review_count: number
  due_count: number
  accuracy: number
  wrong_rate: number
  lapse_count: number
}

export const KP_ANALYTICS_METRIC_FIELDS = [
  'attempt_count',
  'wrong_count',
  'review_count',
  'due_count',
  'accuracy',
  'wrong_rate',
  'lapse_count',
] as const

export type KpAnalyticsMetricField = (typeof KP_ANALYTICS_METRIC_FIELDS)[number]

export type KpAnalyticsListResponse = KpAnalytics[]

export function listKpAnalytics(): Promise<KpAnalyticsListResponse> {
  return apiFetch<KpAnalyticsListResponse>('/api/admin/knowledge-points/analytics')
}
