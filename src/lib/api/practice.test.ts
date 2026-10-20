import { describe, expect, it, vi } from 'vitest'
import {
  getTodayPractice,
  type PracticeEmptyMetadata,
  type PracticeItem,
  type PracticeTodayResponse,
} from './practice'

const PRACTICE_REQUIRED_ITEM_FIELDS = [
  'question_id',
  'knowledge_point_id',
  'selection_reason',
] as const

const PRACTICE_FORBIDDEN_ITEM_FIELDS = [
  'answer_data',
  'correct_answer',
  'analysis',
  'explanation',
] as const

const practiceItemFixture: PracticeItem = {
  question_id: '11111111-1111-1111-1111-111111111111',
  knowledge_point_id: 7,
  selection_reason: 'weak_kp_wrong_rate',
}

const emptyMetadataFixture: PracticeEmptyMetadata = {
  reason: 'candidates_returned',
  raw_candidate_count: 12,
  recent_attempt_excluded_count: 4,
  mastered_excluded_count: 2,
  eligible_candidate_count: 6,
  target_count: 3,
  returned_count: 1,
  window_hours: 168,
}

const practiceTodayFixture: PracticeTodayResponse = {
  items: [practiceItemFixture],
  empty_metadata: emptyMetadataFixture,
}

describe('PracticeItem DTO (W3-D05 / PR-13)', () => {
  it('has exactly the required contract fields and nothing else', () => {
    expect(Object.keys(practiceItemFixture).sort()).toEqual(
      [...PRACTICE_REQUIRED_ITEM_FIELDS].sort(),
    )
  })

  it('never carries answer or explanation fields', () => {
    const keys = Object.keys(practiceItemFixture)
    for (const forbidden of PRACTICE_FORBIDDEN_ITEM_FIELDS) {
      expect(keys).not.toContain(forbidden)
    }
  })

  it('has exactly the backend empty-metadata fields', () => {
    expect(Object.keys(emptyMetadataFixture).sort()).toEqual(
      [
        'reason',
        'raw_candidate_count',
        'recent_attempt_excluded_count',
        'mastered_excluded_count',
        'eligible_candidate_count',
        'target_count',
        'returned_count',
        'window_hours',
      ].sort(),
    )
  })

  it('exposes exactly the items and empty_metadata response fields', () => {
    expect(Object.keys(practiceTodayFixture).sort()).toEqual(['empty_metadata', 'items'])
  })
})

describe('getTodayPractice', () => {
  it('reads the admin practice-today endpoint with admin session credentials', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(practiceTodayFixture), { status: 200 }),
    )

    const response = await getTodayPractice()

    expect(response).toEqual(practiceTodayFixture)
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/admin/practice/today'),
      expect.objectContaining({ credentials: 'include' }),
    )
    fetchMock.mockRestore()
  })
})
