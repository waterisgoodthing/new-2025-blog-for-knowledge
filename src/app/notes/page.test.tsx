import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({ useNoteIndex: vi.fn(), mutate: vi.fn() }))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams()
}))
vi.mock('@/hooks/use-note-index', () => ({ useNoteIndex: mocks.useNoteIndex }))
vi.mock('@/hooks/use-admin-auth', () => ({ useAdminAuth: () => ({ isAdmin: false }) }))
vi.mock('@/lib/api/folders', () => ({ listFolders: vi.fn(), findFolderPath: vi.fn(), moveNoteToFolder: vi.fn() }))
vi.mock('@/lib/api/notes', () => ({ deleteNote: vi.fn() }))
vi.mock('@/lib/render-readiness', () => ({ markRenderReady: vi.fn() }))
vi.mock('./components/knowledge-sidebar', () => ({ KnowledgeSidebar: () => <aside /> }))
vi.mock('./components/suggestion-card', () => ({ SuggestionCard: () => null }))
vi.mock('./components/weekly-summary-card', () => ({ WeeklySummaryCard: () => null }))
vi.mock('@/components/move-to-folder-dialog', () => ({ MoveToFolderDialog: () => null }))
vi.mock('@/components/context-menu', () => ({ ContextMenu: () => null }))

import NotesPage from './page'

describe('/notes async states', () => {
  beforeEach(() => {
    mocks.useNoteIndex.mockReset()
    mocks.mutate.mockReset()
  })

  it('shows a stable loading panel', () => {
    mocks.useNoteIndex.mockReturnValue({ isLoading: true, mutate: mocks.mutate })
    render(<NotesPage />)

    expect(screen.getByRole('status', { name: '正在加载笔记' })).toBeInTheDocument()
  })

	it('shows the safe API error and retries through SWR mutate', () => {
		const apiError = new Error('API 连接失败')
		apiError.name = 'ApiError'
		mocks.useNoteIndex.mockReturnValue({ isLoading: false, error: apiError, mutate: mocks.mutate })
    render(<NotesPage />)

    expect(screen.getByRole('alert')).toHaveTextContent('API 连接失败')
    fireEvent.click(screen.getByRole('button', { name: '重试' }))
    expect(mocks.mutate).toHaveBeenCalledOnce()
  })

  it('does not treat an empty response as an API error', () => {
    mocks.useNoteIndex.mockReturnValue({ isLoading: false, data: { items: [], total: 0 }, mutate: mocks.mutate })
    render(<NotesPage />)

    expect(screen.getByText('暂时没有公开笔记')).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })
})
