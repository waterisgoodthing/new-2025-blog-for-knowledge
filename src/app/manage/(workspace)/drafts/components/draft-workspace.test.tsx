import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'

// Mock API modules
vi.mock('@/lib/api/drafts', () => ({
  listDrafts: vi.fn(),
  createQuestionDraft: vi.fn(),
}))

vi.mock('@/lib/api/mistakes', () => ({
  listMistakeDrafts: vi.fn(),
  createMistakeDraft: vi.fn(),
}))

vi.mock('@/lib/api/questions', () => ({
  listQuestions: vi.fn(),
}))

vi.mock('@/lib/api/taxonomy', () => ({
  listSubjects: vi.fn(),
  listKnowledgePoints: vi.fn(),
}))

// Mock Link component
vi.mock('next/link', () => ({
  default: ({
    href,
    children,
    ...props
  }: {
    href: string
    children: React.ReactNode
    [key: string]: unknown
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}))

const { listDrafts } = await import('@/lib/api/drafts')
const { listMistakeDrafts } = await import('@/lib/api/mistakes')
const { DraftWorkspace } = await import('./draft-workspace')

describe('DraftWorkspace — partial failure handling (R-04 / P1-04)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows error (not empty) when question drafts fail and mistake drafts return empty', async () => {
    vi.mocked(listDrafts).mockRejectedValue(new Error('网络请求失败'))
    vi.mocked(listMistakeDrafts).mockResolvedValue([])

    render(<DraftWorkspace />)

    await waitFor(() => {
      expect(screen.getByText('网络请求失败')).toBeInTheDocument()
    })

    // Should NOT show "当前没有草稿" (empty state)
    expect(screen.queryByText('当前没有草稿。')).not.toBeInTheDocument()

    // Should show retry button
    expect(screen.getByRole('button', { name: '重试' })).toBeInTheDocument()
  })

  it('shows error when both sources fail', async () => {
    vi.mocked(listDrafts).mockRejectedValue(new Error('题目草稿加载失败'))
    vi.mocked(listMistakeDrafts).mockRejectedValue(new Error('错题草稿加载失败'))

    render(<DraftWorkspace />)

    await waitFor(() => {
      expect(screen.getByText(/题目草稿加载失败/)).toBeInTheDocument()
      expect(screen.getByText(/错题草稿加载失败/)).toBeInTheDocument()
    })

    expect(screen.queryByText('当前没有草稿。')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: '重试' })).toBeInTheDocument()
  })

  it('shows list when one source succeeds and other fails', async () => {
    vi.mocked(listDrafts).mockRejectedValue(new Error('题目草稿加载失败'))
    vi.mocked(listMistakeDrafts).mockResolvedValue([
      {
        id: 'md-1',
        draft_item_id: 'draft-1',
        question_id: null,
        question_draft_id: null,
        subject_id: 1,
        title: '测试错题',
        question_text: '问题内容',
        my_answer: null,
        correct_answer_snapshot: null,
        explanation_snapshot: null,
        reason_category: 'concept',
        mistake_reason: null,
        difficulty: null,
        knowledge_point_ids: [],
        status: 'pending',
        version: 1,
        target_id: null,
        created_at: '2026-07-12T10:00:00Z',
        updated_at: '2026-07-12T10:00:00Z',
      },
    ])

    render(<DraftWorkspace />)

    await waitFor(() => {
      expect(screen.getByText('测试错题')).toBeInTheDocument()
    })

    // Should also show the error banner for the failed source
    expect(screen.getByText('题目草稿加载失败')).toBeInTheDocument()

    // Should NOT show empty state
    expect(screen.queryByText('当前没有草稿。')).not.toBeInTheDocument()
  })

  it('shows empty state when both sources succeed with no data', async () => {
    vi.mocked(listDrafts).mockResolvedValue([])
    vi.mocked(listMistakeDrafts).mockResolvedValue([])

    render(<DraftWorkspace />)

    await waitFor(() => {
      expect(screen.getByText('当前没有草稿。')).toBeInTheDocument()
    })

    expect(screen.queryByText('重试')).not.toBeInTheDocument()
  })

  it('retries on retry button click', async () => {
    vi.mocked(listDrafts).mockRejectedValueOnce(new Error('第一次失败'))
    vi.mocked(listMistakeDrafts).mockResolvedValue([])

    render(<DraftWorkspace />)

    await waitFor(() => {
      expect(screen.getByText('第一次失败')).toBeInTheDocument()
    })

    // Fix the mock for retry
    vi.mocked(listDrafts).mockResolvedValueOnce([])
    vi.mocked(listMistakeDrafts).mockResolvedValueOnce([])

    fireEvent.click(screen.getByRole('button', { name: '重试' }))

    await waitFor(() => {
      expect(screen.getByText('当前没有草稿。')).toBeInTheDocument()
    })
  })
})
