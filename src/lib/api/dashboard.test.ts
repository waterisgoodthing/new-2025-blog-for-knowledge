import { describe, expect, it, vi } from 'vitest'

import {
  getDashboardSummary,
  type DashboardSectionAction,
  type DashboardSummary,
  type DashboardTodayFirstAction,
  type DashboardWeakKnowledgePoint,
} from './dashboard'

const WEAK_KP_FIELDS = [
  'knowledge_point_id',
  'name',
  'attempt_count',
  'wrong_rate',
  'lapse_count',
  'due_count',
] as const

const SECTION_ACTION_FIELDS = [
  'section',
  'count',
  'available',
  'target_route',
  'reason',
] as const

const FIRST_ACTION_FIELDS = [
  'kind',
  'count',
  'target_route',
  'reason',
] as const

const LOCKED_DELTA_FIELDS = [
  'review_today_count',
  'practice_today_count',
  'weak_top3',
  'recently_mastered_4',
  'today_first_action',
  'section_actions',
] as const

const weakFixture: DashboardWeakKnowledgePoint = {
  knowledge_point_id: 7,
  name: '导数',
  attempt_count: 9,
  wrong_rate: 0.5,
  lapse_count: 2,
  due_count: 3,
}

const reviewActionFixture: DashboardSectionAction = {
  section: 'review',
  count: 2,
  available: true,
  target_route: '/manage/review',
  reason: 'due_reviews_pending',
}

const practiceActionFixture: DashboardSectionAction = {
  section: 'practice',
  count: 4,
  available: true,
  target_route: '/manage/practice',
  reason: 'practice_available',
}

const firstActionFixture: DashboardTodayFirstAction = {
  kind: 'review',
  count: 2,
  target_route: '/manage/review',
  reason: 'due_reviews_first',
}

const summaryFixture = {
  generated_at: '2026-09-25T10:00:00Z',
  counts: { questions: 1, mistakes: 1, knowledge_points: 1, attachments: 0, due_reviews: 2 },
  recent_questions: [],
  recent_mistakes: [],
  recent_reviews: [],
  sections: { learning: 'ready', activity: 'ready', storage: 'ready' },
  system: { service: 'ok', database: 'ok', storage: 'ok' },
  review_today_count: 2,
  practice_today_count: 4,
  weak_top3: [weakFixture],
  recently_mastered_4: [],
  today_first_action: firstActionFixture,
  section_actions: { review: reviewActionFixture, practice: practiceActionFixture },
} satisfies DashboardSummary

describe('DashboardSummary DTO (PR-11 delta)', () => {
  it('carries exactly the locked delta fields', () => {
    for (const field of LOCKED_DELTA_FIELDS) {
      expect(summaryFixture).toHaveProperty(field)
    }
  })

  it('maps weak knowledge points and section actions to the backend contract', () => {
    expect(Object.keys(weakFixture).sort()).toEqual([...WEAK_KP_FIELDS].sort())
    expect(Object.keys(reviewActionFixture).sort()).toEqual([...SECTION_ACTION_FIELDS].sort())
    expect(Object.keys(practiceActionFixture).sort()).toEqual([...SECTION_ACTION_FIELDS].sort())
  })

  it('keeps the deterministic first action shape without AI fields', () => {
    expect(Object.keys(firstActionFixture).sort()).toEqual([...FIRST_ACTION_FIELDS].sort())
    expect(Object.keys(summaryFixture.today_first_action)).not.toContain('ai_generated')
  })
})

describe('getDashboardSummary', () => {
  it('reads the admin dashboard summary endpoint with session credentials', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(new Response(JSON.stringify(summaryFixture), { status: 200 }))

    const response = await getDashboardSummary()

    expect(response).toEqual(summaryFixture)
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/admin/dashboard/summary'),
      expect.objectContaining({ credentials: 'include' }),
    )
    fetchMock.mockRestore()
  })
})
