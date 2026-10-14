import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import NotesPage from './page'

const mocks = vi.hoisted(() => ({ useNoteIndex: vi.fn(), deleteNote: vi.fn(), mutate: vi.fn() }))

vi.mock('next/navigation', () => ({ useSearchParams: () => new URLSearchParams() }))
vi.mock('@/hooks/use-note-index', () => ({ useNoteIndex: mocks.useNoteIndex }))
vi.mock('@/lib/api/notes', () => ({ deleteNote: mocks.deleteNote }))
vi.mock('swr', () => ({ useSWRConfig: () => ({ mutate: mocks.mutate }) }))

describe('NotesPage', () => {
	beforeEach(() => {
		mocks.useNoteIndex.mockReset()
		mocks.deleteNote.mockReset()
		mocks.mutate.mockReset()
	})

	it('revalidates through FeatureState when loading fails', async () => {
		const revalidate = vi.fn()
		mocks.useNoteIndex.mockReturnValue({ error: new Error('offline'), isLoading: false, data: undefined, mutate: revalidate })
		render(<NotesPage />)
		fireEvent.click(screen.getByRole('button', { name: '重新尝试' }))
		await waitFor(() => expect(revalidate).toHaveBeenCalledOnce())
	})

	it('surfaces deletion failures instead of leaving an unhandled rejection', async () => {
		mocks.useNoteIndex.mockReturnValue({
			data: { items: [{ slug: 'hello', title: 'Hello', type: 'blog', status: 'draft', updated_at: '2026-01-01T00:00:00Z' }], total: 1, page: 1, size: 20 },
			isLoading: false,
			mutate: vi.fn()
		})
		mocks.deleteNote.mockRejectedValueOnce(new Error('delete failed'))
		vi.spyOn(window, 'confirm').mockReturnValue(true)
		render(<NotesPage />)
		fireEvent.click(screen.getByRole('button', { name: '删除' }))
		await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('delete failed'))
	})

	it('requests note and blog server-side instead of filtering legacy rows', () => {
		mocks.useNoteIndex.mockReturnValue({
			data: {
				items: [
					{ slug: 'note-one', title: 'Note', type: 'note', status: 'draft', updated_at: '2026-01-01T00:00:00Z' }
				],
				total: 1,
				page: 1,
				size: 30
			},
			isLoading: false,
			mutate: vi.fn()
		})

		render(<NotesPage />)

		expect(screen.getByText('Note')).toBeInTheDocument()
		const params = mocks.useNoteIndex.mock.calls[0][0]
		// The workspace excludes legacy mistake rows on the server, not by
		// dropping a single client page.
		expect(params.types).toBe('note,blog')
		expect(params.type).toBeUndefined()
		expect(params.size).toBe(30)
	})
})
