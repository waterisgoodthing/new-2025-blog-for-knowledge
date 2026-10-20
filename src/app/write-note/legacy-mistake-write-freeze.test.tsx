import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  noteData: undefined as unknown,
  getNote: vi.fn(),
  getNoteVersions: vi.fn(),
  updateNote: vi.fn(),
  uploadImage: vi.fn(),
  listCategories: vi.fn(),
  listSubjects: vi.fn(),
  toastError: vi.fn(),
}))

vi.mock('next/navigation', () => ({
  useParams: () => ({ slug: 'legacy-mistake-note' }),
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}))
vi.mock('next/dynamic', () => ({ default: () => () => null }))
vi.mock('swr', () => ({
  default: (key: string, fetcher: () => unknown) => {
    void key
    void fetcher
    return { data: mocks.noteData, isLoading: false }
  },
}))
vi.mock('motion/react', () => ({
  motion: new Proxy({}, {
    get: () => ({ children, initial, animate, transition, ...rest }: Record<string, unknown> & { children?: unknown }) => (
      <div {...rest}>{children as never}</div>
    ),
  }),
}))
vi.mock('sonner', () => ({
  toast: {
    error: (...args: unknown[]) => mocks.toastError(...args),
    success: vi.fn(),
    warning: vi.fn(),
  },
}))
vi.mock('@/lib/api/notes', () => ({
  getNote: mocks.getNote,
  getNoteVersions: mocks.getNoteVersions,
  updateNote: mocks.updateNote,
  uploadImage: mocks.uploadImage,
}))
vi.mock('@/lib/api/meta', () => ({
  listCategories: mocks.listCategories,
  listSubjects: mocks.listSubjects,
}))
vi.mock('./hooks/use-note-editor-tab', () => ({
  useNoteEditorTab: () => ({ tab: 'write', setTab: vi.fn() }),
}))
vi.mock('./hooks/use-note-editor', () => ({
  useNoteEditor: () => ({
    handleKeyDown: vi.fn(),
    handleChange: vi.fn(),
    handlePaste: vi.fn(),
    insertText: vi.fn(),
    wrapSelection: vi.fn(),
    slashState: null,
    closeSlash: vi.fn(),
    executeSlash: vi.fn(),
  }),
}))
vi.mock('./components/note-toolbar', () => ({ NoteToolbar: () => null }))
vi.mock('./components/note-templates', () => ({ NoteTemplatesDropdown: () => null }))
vi.mock('./components/slash-command-menu', () => ({ SlashCommandMenu: () => null }))
vi.mock('./components/ai-assistant-panel', () => ({ AIAssistantPanel: () => null }))
vi.mock('@/components/tag-suggestion-dialog', () => ({ TagSuggestionDialog: () => null }))
vi.mock('@/components/auth-gate', () => ({
  AuthGate: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

import EditNotePage from './[slug]/page'

const mistakeNote = {
  id: 'n-1',
  slug: 'legacy-mistake-note',
  title: '旧错题',
  type: 'mistake',
  status: 'published',
  hidden: false,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-02T00:00:00Z',
  tags: [],
  sort_order: 0,
  revision: 3,
  content: '',
  question: 'Q',
  my_answer: 'SECRET_MY_ANSWER',
  correct_answer: 'B',
  analysis: 'A',
  knowledge_points: 'KP',
  difficulty: 'medium',
  images: [],
  ai_metadata: null,
}

const plainNote = { ...mistakeNote, id: 'n-2', slug: 'plain', type: 'note', my_answer: undefined }

describe('write-note legacy mistake freeze (W3-D09 F-6)', () => {
  beforeEach(() => {
    mocks.getNote.mockReset()
    mocks.getNoteVersions.mockReset().mockResolvedValue([])
    mocks.updateNote.mockReset()
    mocks.uploadImage.mockReset()
    mocks.listCategories.mockReset().mockResolvedValue([])
    mocks.listSubjects.mockReset().mockResolvedValue([])
    mocks.toastError.mockReset()
  })

  it('disables save and shows the frozen notice when editing type=mistake', async () => {
    mocks.noteData = mistakeNote
    render(<EditNotePage />)

    expect(await screen.findByTestId('legacy-mistake-write-frozen')).toHaveTextContent(
      'legacy 错题写入已冻结，请使用 canonical 错题流程',
    )
    const save = screen.getByTestId('legacy-mistake-save-disabled')
    expect(save).toBeDisabled()
    expect(save).toHaveTextContent('保存（已冻结）')
  })

  it('fail-closes updateNote for mistake rows even if save is triggered', async () => {
    mocks.noteData = mistakeNote
    render(<EditNotePage />)

    const save = await screen.findByTestId('legacy-mistake-save-disabled')
    fireEvent.click(save)
    await waitFor(() => expect(mocks.updateNote).not.toHaveBeenCalled())
  })

  it('keeps saving enabled for non-mistake notes', async () => {
    mocks.noteData = plainNote
    render(<EditNotePage />)

    const save = await screen.findByRole('button', { name: '保存' })
    expect(save).not.toBeDisabled()
    expect(screen.queryByTestId('legacy-mistake-write-frozen')).not.toBeInTheDocument()
  })
})
