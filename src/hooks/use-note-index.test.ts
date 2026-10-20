import { describe, expect, it, vi } from 'vitest'

const swrMock = vi.fn((key: string | null) => ({ key }))

vi.mock('swr', () => ({ default: swrMock }))
vi.mock('@/lib/api/notes', () => ({ listNotes: vi.fn() }))
vi.mock('@/lib/api/review', () => ({
  getReviewPlan: vi.fn(),
  getReviewStats: vi.fn(),
}))

const { useReviewPlan, useReviewStats } = await import('./use-note-index')

describe('public mistake review API gate', () => {
  it('disables review stats and plan requests for anonymous users', () => {
    swrMock.mockClear()

    useReviewStats(false)
    useReviewPlan(false)

    expect(swrMock).toHaveBeenNthCalledWith(
      1,
      null,
      expect.any(Function),
      expect.any(Object),
    )
    expect(swrMock).toHaveBeenNthCalledWith(
      2,
      null,
      expect.any(Function),
      expect.any(Object),
    )
  })

  it('enables review stats and plan requests for administrators', () => {
    swrMock.mockClear()

    useReviewStats(true)
    useReviewPlan(true)

    expect(swrMock).toHaveBeenNthCalledWith(
      1,
      '/api/review/stats',
      expect.any(Function),
      expect.any(Object),
    )
    expect(swrMock).toHaveBeenNthCalledWith(
      2,
      '/api/review/plan',
      expect.any(Function),
      expect.any(Object),
    )
  })
})
