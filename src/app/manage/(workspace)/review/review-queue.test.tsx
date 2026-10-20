import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { ReviewQueue } from './review-queue'

vi.mock('@/lib/api/review-items', () => ({
  listDueReviewItems: vi.fn(async () => [
    {
      id: 'item-1',
      target_type: 'mistake',
      target_id: 'mistake-1',
      state: 'active',
      algorithm: 'fixed_interval_v2',
      interval_days: 3,
      repetitions: 1,
      next_review_at: '2026-09-20T00:00:00+00:00',
      last_reviewed_at: null,
      last_rating: 4,
      question_text: '单调性错题',
      mistake_reason: null,
    },
  ]),
  listReviewRecords: vi.fn(async () => [
    {
      id: 'rec-1',
      review_item_id: 'item-1',
      rating: 4,
      reviewed_at: '2026-09-19T00:00:00+00:00',
      previous_interval_days: 1,
      next_interval_days: 3,
      previous_next_review_at: '2026-09-19T00:00:00+00:00',
      next_review_at: '2026-09-20T00:00:00+00:00',
      previous_state: 'active',
      new_state: 'active',
      attempt_id: 'attempt-9',
      created_at: '2026-09-19T00:00:00+00:00',
    },
  ]),
  submitReview: vi.fn(async () => ({
    id: 'item-1',
    next_review_at: '2026-09-27T00:00:00+00:00',
  })),
}))

vi.mock('@/lib/api/mistakes', () => ({
  getMistake: vi.fn(async () => ({ id: 'mistake-1', question_id: 'question-1' })),
}))

vi.mock('@/lib/api/questions', () => ({
  getQuestion: vi.fn(async () => ({
    id: 'question-1',
    question_type: 'single_choice',
    options: [
      { key: 'A', text: 'a' },
      { key: 'B', text: 'b' },
    ],
  })),
}))

vi.mock('@/lib/api/attempts', () => ({
  submitReanswer: vi.fn(async () => ({
    attempt: { id: 'attempt-1' },
    evaluation: { verdict: 'correct', recommendation: 4 },
  })),
}))

vi.mock('@/lib/manage-display', () => ({
  formatChineseDateTime: (value: string) => value,
}))

import { submitReview } from '@/lib/api/review-items'
import { submitReanswer, type ReanswerResult } from '@/lib/api/attempts'
import { getQuestion, type Question } from '@/lib/api/questions'

describe('ReviewQueue PR-08', () => {
  it('renders all six rating grades with a keyboard hint (no grade swallowed)', async () => {
    render(<ReviewQueue />)
    const group = await screen.findByRole('group', { name: /六档评分/ })
    const buttons = within(group).getAllByRole('button')
    expect(buttons.map((button) => button.textContent)).toEqual(['0', '1', '2', '3', '4', '5'])
  })

  it('keyboard 0-5 submits the matching grade', async () => {
    render(<ReviewQueue />)
    const group = await screen.findByRole('group', { name: /六档评分/ })
    fireEvent.keyDown(group, { key: '4' })
    await waitFor(() =>
      expect(submitReview).toHaveBeenCalledWith('item-1', 4, '2026-09-20T00:00:00+00:00', undefined),
    )
  })

  it('runs Mistake -> Re-answer -> Evaluation -> Recommendation -> Confirm with attempt linkage', async () => {
    render(<ReviewQueue />)
    fireEvent.click(await screen.findByRole('button', { name: '再答' }))
    // options rendered from the fetched question
    fireEvent.click(await screen.findByRole('button', { name: 'B. b' }))
    fireEvent.click(screen.getByRole('button', { name: '提交作答' }))

    expect(await screen.findByText(/判定：作答正确/)).toBeInTheDocument()
    expect(screen.getByText(/建议评分 4 分/)).toBeInTheDocument()
    expect(submitReanswer).toHaveBeenCalledWith('question-1', 'B')

    // recommendation preselected but overridable; confirm carries the attempt id
    const recommended = screen.getByRole('button', { name: '提交 4 分复习结果（机器推荐）' })
    expect(recommended).toHaveAttribute('aria-pressed', 'true')
    fireEvent.click(screen.getByRole('button', { name: '提交 5 分复习结果' }))
    await waitFor(() =>
      expect(submitReview).toHaveBeenCalledWith('item-1', 5, '2026-09-20T00:00:00+00:00', 'attempt-1'),
    )
    // ordinary success toast, never an undo control (PR-24 not authorized)
    expect(await screen.findByText(/已提交复习/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /撤销/ })).not.toBeInTheDocument()
  })

  it('lets multiple_choice answers toggle and submits a stable option-ordered set', async () => {
    vi.mocked(getQuestion).mockResolvedValueOnce({
      id: 'question-1',
      question_type: 'multiple_choice',
      options: [
        { key: 'A', text: 'a' },
        { key: 'B', text: 'b' },
        { key: 'C', text: 'c' },
      ],
    } as never)
    render(<ReviewQueue />)
    fireEvent.click(await screen.findByRole('button', { name: '再答' }))
    const a = await screen.findByRole('button', { name: 'A. a' })
    const c = screen.getByRole('button', { name: 'C. c' })
    // empty set cannot submit
    expect(screen.getByRole('button', { name: '提交作答' })).toBeDisabled()
    fireEvent.click(c)
    fireEvent.click(a)
    expect(a).toHaveAttribute('aria-pressed', 'true')
    expect(c).toHaveAttribute('aria-pressed', 'true')
    fireEvent.click(screen.getByRole('button', { name: '提交作答' }))
    await waitFor(() => expect(submitReanswer).toHaveBeenCalledWith('question-1', 'A,C'))
  })

  it('clears a prior evaluation when the answer is edited', async () => {
    vi.mocked(getQuestion).mockResolvedValueOnce({
      id: 'question-1',
      question_type: 'multiple_choice',
      options: [
        { key: 'A', text: 'a' },
        { key: 'B', text: 'b' },
      ],
    } as never)
    render(<ReviewQueue />)
    fireEvent.click(await screen.findByRole('button', { name: '再答' }))
    fireEvent.click(await screen.findByRole('button', { name: 'A. a' }))
    fireEvent.click(screen.getByRole('button', { name: '提交作答' }))
    expect(await screen.findByText(/判定：作答正确/)).toBeInTheDocument()
    // editing the answer resets to the editing phase, dropping the stale recommendation
    fireEvent.click(screen.getByRole('button', { name: 'B. b' }))
    expect(screen.queryByText(/建议评分/)).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: '提交作答' })).toBeEnabled()
  })

  it('marks records that carry a re-answer attempt', async () => {
    render(<ReviewQueue />)
    fireEvent.click(await screen.findByRole('button', { name: '记录' }))
    expect(await screen.findByText(/评分 4.*含再答/)).toBeInTheDocument()
  })

  it('drops a late reanswer evaluation after collapse and reopen (EV01 race)', async () => {
    vi.mocked(submitReview).mockClear()
    let release: ((value: ReanswerResult | PromiseLike<ReanswerResult>) => void) | undefined
    vi.mocked(submitReanswer).mockImplementationOnce(
      () => new Promise((resolve) => { release = resolve }),
    )
    render(<ReviewQueue />)

    fireEvent.click(await screen.findByRole('button', { name: '再答' }))
    fireEvent.click(await screen.findByRole('button', { name: 'A. a' }))
    fireEvent.click(screen.getByRole('button', { name: '提交作答' }))

    // While A is in flight, collapse and reopen the same item and choose B.
    fireEvent.click(screen.getByRole('button', { name: '收起' }))
    fireEvent.click(await screen.findByRole('button', { name: '再答' }))
    fireEvent.click(await screen.findByRole('button', { name: 'B. b' }))

    await act(async () => {
      release?.({ attempt: { id: 'attempt-A' }, evaluation: { verdict: 'correct', recommendation: 4 } } as never)
    })

    // The stale A verdict must never surface and B is still pending a score.
    expect(screen.queryByText(/建议评分/)).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: '提交作答' })).toBeEnabled()

    // Confirming B must NOT carry the old A attempt id.
    fireEvent.click(screen.getByRole('button', { name: '提交 5 分复习结果' }))
    await waitFor(() =>
      expect(submitReview).toHaveBeenCalledWith('item-1', 5, '2026-09-20T00:00:00+00:00', undefined),
    )
  })

  it('ignores a stale error from a request that was superseded (EV01 race)', async () => {
    vi.mocked(submitReanswer).mockImplementationOnce(
      () => new Promise((_resolve, reject) => { setTimeout(() => reject(new Error('late failure')), 5) }),
    )
    render(<ReviewQueue />)

    fireEvent.click(await screen.findByRole('button', { name: '再答' }))
    fireEvent.click(await screen.findByRole('button', { name: 'A. a' }))
    fireEvent.click(screen.getByRole('button', { name: '提交作答' }))
    fireEvent.click(screen.getByRole('button', { name: '收起' }))

    await act(async () => { await new Promise((resolve) => setTimeout(resolve, 20)) })

    // The stale rejection belongs to a closed panel and must not be shown.
    expect(screen.queryByText(/提交作答失败/)).not.toBeInTheDocument()
    expect(screen.queryByText('late failure')).not.toBeInTheDocument()
  })

  it('ignores an out-of-order question load after the panel is reopened (EV01 race)', async () => {
    vi.mocked(getQuestion).mockClear()
    let releaseFirst: ((value: Question | PromiseLike<Question>) => void) | undefined
    vi.mocked(getQuestion)
      .mockImplementationOnce(() => new Promise((resolve) => { releaseFirst = resolve }))
      .mockResolvedValueOnce({
        id: 'question-2',
        question_type: 'single_choice',
        options: [
          { key: 'A', text: 'a' },
          { key: 'B', text: 'b' },
        ],
      } as never)

    render(<ReviewQueue />)
    fireEvent.click(await screen.findByRole('button', { name: '再答' }))
    // Ensure the first question load is actually in flight before we close it.
    await waitFor(() => expect(getQuestion).toHaveBeenCalledTimes(1))
    fireEvent.click(screen.getByRole('button', { name: '收起' }))
    fireEvent.click(await screen.findByRole('button', { name: '再答' }))

    expect(await screen.findByRole('button', { name: 'B. b' })).toBeInTheDocument()

    await act(async () => {
      releaseFirst?.({
        id: 'question-stale',
        question_type: 'single_choice',
        options: [{ key: 'Z', text: 'z' }],
      } as never)
    })

    expect(screen.queryByRole('button', { name: 'Z. z' })).not.toBeInTheDocument()
  })
})
