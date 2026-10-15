import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { ComponentProps, ReactNode } from 'react'

const mocks = vi.hoisted(() => ({
  listPublicMistakes: vi.fn(),
  useNoteIndex: vi.fn(),
  listNotes: vi.fn(),
  useReviewStats: vi.fn(),
  useReviewPlan: vi.fn(),
  useAdminAuth: vi.fn(),
}))

vi.mock('next/link', () => ({
  default: ({ href, children, ...rest }: { href: string; children: ReactNode } & ComponentProps<'a'>) => (
    <a href={href} {...rest}>{children}</a>
  ),
}))
vi.mock('motion/react', () => ({
  motion: {
    h1: ({ children, initial, animate, ...rest }: Record<string, unknown> & { children?: ReactNode }) => (
      <h1 {...(rest as ComponentProps<'h1'>)}>{children}</h1>
    ),
    article: ({ children, initial, animate, transition, ...rest }: Record<string, unknown> & { children?: ReactNode }) => (
      <article {...(rest as ComponentProps<'article'>)}>{children}</article>
    ),
  },
}))
vi.mock('@/lib/api/mistakes', () => ({ listPublicMistakes: mocks.listPublicMistakes }))
vi.mock('@/lib/api/notes', () => ({ listNotes: mocks.listNotes }))
vi.mock('@/hooks/use-note-index', () => ({
  useNoteIndex: mocks.useNoteIndex,
  useReviewStats: mocks.useReviewStats,
  useReviewPlan: mocks.useReviewPlan,
}))
vi.mock('@/hooks/use-admin-auth', () => ({ useAdminAuth: mocks.useAdminAuth }))
vi.mock('./components/weak-point-diagnosis', () => ({ WeakPointDiagnosis: () => null }))

import MistakesPage from './page'

const publicItem = {
  id: 'p-1',
  title: '牛顿第二定律综合题',
  question_text: '一个物体受合外力 F 作用…',
  correct_answer: 'B',
  analysis: '由 F=ma 可得…',
  reason_category: 'concept',
  mistake_reason: '概念理解偏差',
  difficulty: 'medium',
  knowledge_point_ids: [7],
  created_at: '2026-09-01T00:00:00Z',
  updated_at: '2026-09-02T00:00:00Z',
}

describe('/mistakes canonical public list (PR-09)', () => {
  beforeEach(() => {
    mocks.listPublicMistakes.mockReset()
    mocks.useNoteIndex.mockReset()
    mocks.listNotes.mockReset()
    mocks.useReviewStats.mockReturnValue({ data: undefined })
    mocks.useReviewPlan.mockReturnValue({ data: undefined })
    mocks.useAdminAuth.mockReturnValue({ isAdmin: false })
  })

  it('shows the loading panel while the public list is in flight', () => {
    mocks.listPublicMistakes.mockReturnValue(new Promise(() => {}))
    render(<MistakesPage />)

    expect(screen.getByRole('status', { name: '正在加载公开错题' })).toBeInTheDocument()
  })

  it('renders canonical cards without any my_answer field', async () => {
    mocks.listPublicMistakes.mockResolvedValue({
      items: [{ ...publicItem, my_answer: 'SECRET_PRIVATE_ANSWER' }],
      total: 1,
      page: 1,
      size: 20,
      empty: false,
      message: null,
    })
    const { container } = render(<MistakesPage />)

    await screen.findByText('牛顿第二定律综合题')
    expect(screen.getByText('一个物体受合外力 F 作用…')).toBeInTheDocument()
    expect(screen.getByText('B')).toBeInTheDocument()
    expect(screen.getByText('由 F=ma 可得…')).toBeInTheDocument()
    expect(screen.getByText('概念理解偏差')).toBeInTheDocument()
    expect(container.textContent).not.toContain('SECRET_PRIVATE_ANSWER')
    expect(container.textContent).not.toContain('我的答案')
  })

  it('does not link cards to legacy note slugs', async () => {
    mocks.listPublicMistakes.mockResolvedValue({
      items: [publicItem],
      total: 1,
      page: 1,
      size: 20,
      empty: false,
      message: null,
    })
    const { container } = render(<MistakesPage />)

    await screen.findByText('牛顿第二定律综合题')
    const hrefs = Array.from(container.querySelectorAll('a')).map((a) => a.getAttribute('href') ?? '')
    expect(hrefs.filter((href) => href.startsWith('/notes/'))).toEqual([])
  })

  it('renders an explicit Empty state when zero public mistakes are returned', async () => {
    mocks.listPublicMistakes.mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      size: 20,
      empty: true,
      message: '当前没有公开错题',
    })
    render(<MistakesPage />)

    expect(await screen.findByText('当前没有公开错题')).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('shows API errors with retry and never falls back to the legacy note index', async () => {
    const apiError = new Error('服务暂时不可用')
    apiError.name = 'ApiError'
    mocks.listPublicMistakes.mockRejectedValueOnce(apiError).mockResolvedValueOnce({
      items: [publicItem],
      total: 1,
      page: 1,
      size: 20,
      empty: false,
      message: null,
    })
    render(<MistakesPage />)

    expect(await screen.findByRole('alert')).toHaveTextContent('服务暂时不可用')
    fireEvent.click(screen.getByRole('button', { name: '重试' }))

    await screen.findByText('牛顿第二定律综合题')
    expect(mocks.listPublicMistakes).toHaveBeenCalledTimes(2)
    expect(mocks.useNoteIndex).not.toHaveBeenCalled()
    expect(mocks.listNotes).not.toHaveBeenCalled()
  })
})
