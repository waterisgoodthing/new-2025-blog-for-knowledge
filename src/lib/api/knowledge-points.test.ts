import { describe, expect, it, vi } from 'vitest'
import {
  KP_ANALYTICS_METRIC_FIELDS,
  listKpAnalytics,
  type KpAnalytics,
  type KpAnalyticsListResponse,
} from './knowledge-points'

const BACKEND_SCHEMA_FIELDS = [
  'knowledge_point_id',
  'attempt_count',
  'wrong_count',
  'review_count',
  'due_count',
  'accuracy',
  'wrong_rate',
  'lapse_count',
] as const

const kpAnalyticsFixture: KpAnalytics = {
  knowledge_point_id: 7,
  attempt_count: 4,
  wrong_count: 1,
  review_count: 3,
  due_count: 1,
  accuracy: 0.75,
  wrong_rate: 0.25,
  lapse_count: 2,
}

describe('KpAnalytics DTO (W3-D05)', () => {
  it('has exactly the backend schema fields and nothing else', () => {
    expect(Object.keys(kpAnalyticsFixture).sort()).toEqual([...BACKEND_SCHEMA_FIELDS].sort())
  })

  it('exposes exactly the seven backend metric fields', () => {
    expect([...KP_ANALYTICS_METRIC_FIELDS].sort()).toEqual([
      'accuracy',
      'attempt_count',
      'due_count',
      'lapse_count',
      'review_count',
      'wrong_count',
      'wrong_rate',
    ])
  })
})

describe('listKpAnalytics', () => {
  it('reads the admin analytics endpoint with admin session credentials', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify([kpAnalyticsFixture]), { status: 200 }),
    )

    const response: KpAnalyticsListResponse = await listKpAnalytics()

    expect(response).toEqual([kpAnalyticsFixture])
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/admin/knowledge-points/analytics'),
      expect.objectContaining({ credentials: 'include' }),
    )
    fetchMock.mockRestore()
  })
})
