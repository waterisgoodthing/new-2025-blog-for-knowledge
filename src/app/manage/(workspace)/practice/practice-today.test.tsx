import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { PracticeTodayResponse } from '@/lib/api/practice'

vi.mock('@/lib/api/practice', () => ({
  getTodayPractice: vi.fn(),
}))

const { getTodayPractice } = await import('@/lib/api/practice')
const { PracticeToday, selectionReasonText } = await import('./practice-today')

const populated: PracticeTodayResponse = {
  items: [
    { question_id: '11111111-1111-1111-1111-111111111111', knowledge_point_id: 7, selection_reason: 'weak_kp_wrong_rate' },
    { question_id: '22222222-2222-2222-2222-222222222222', knowledge_point_id: 3, selection_reason: 'weak_kp_lapse' },
  ],
  empty_metadata: {
    reason: 'candidates_returned',
    raw_candidate_count: 12,
    recent_attempt_excluded_count: 4,
    mastered_excluded_count: 2,
    eligible_candidate_count: 6,
    target_count: 3,
    returned_count: 2,
    window_hours: 168,
  },
}

const empty: PracticeTodayResponse = {
  items: [],
  empty_metadata: { ...populated.empty_metadata, reason: 'no_eligible_candidates', returned_count: 0 },
}

const mockGetTodayPractice = vi.mocked(getTodayPractice)

describe('PracticeToday', () => {
  beforeEach(() => {
    mockGetTodayPractice.mockReset()
  })

  it('shows a reduced-motion safe loading state while fetching', () => {
    mockGetTodayPractice.mockReturnValue(new Promise(() => {}))
    render(<PracticeToday />)

    expect(screen.getByRole('status', { name: '正在加载今日练习' })).toBeInTheDocument()
  })

  it('renders canonical practice items linked to their questions', async () => {
    mockGetTodayPractice.mockResolvedValue(populated)
    render(<PracticeToday />)

    expect(await screen.findByText('共 2 道练习，均来自薄弱知识点。')).toBeInTheDocument()
    const links = screen.getAllByRole('link', { name: '打开题目' })
    expect(links).toHaveLength(2)
    expect(links[0]).toHaveAttribute('href', '/manage/questions/11111111-1111-1111-1111-111111111111')
    expect(screen.getByText(`选题理由：${selectionReasonText('weak_kp_wrong_rate')}`)).toBeInTheDocument()
  })

  it('is honest when there are no eligible practice items', async () => {
    mockGetTodayPractice.mockResolvedValue(empty)
    render(<PracticeToday />)

    expect(await screen.findByRole('heading', { name: '今日暂无合适练习' })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: '打开题目' })).not.toBeInTheDocument()
  })

  it('retries after a failure and focuses the result region on success', async () => {
    mockGetTodayPractice.mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce(populated)
    render(<PracticeToday />)

    expect(await screen.findByRole('heading', { name: '今日练习加载失败' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '重新尝试' }))

    await waitFor(() => expect(screen.getByRole('region', { name: '今日练习结果' })).toHaveFocus())
    expect(mockGetTodayPractice).toHaveBeenCalledTimes(2)
  })
})
