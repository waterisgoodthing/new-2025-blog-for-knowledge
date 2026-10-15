import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ContentEditor } from './content-editor'

const mocks = vi.hoisted(() => ({ createNote: vi.fn(), updateNote: vi.fn() }))

vi.mock('@/lib/api/notes', () => ({ createNote: mocks.createNote, updateNote: mocks.updateNote }))
vi.mock('@/lib/api/meta', () => ({ listCategories: vi.fn().mockResolvedValue([]) }))

describe('ContentEditor', () => {
	beforeEach(() => {
		mocks.createNote.mockReset()
		mocks.updateNote.mockReset()
		window.history.replaceState({}, '', '/manage/notes/new?type=note')
	})

	it('creates once, transitions to the canonical edit identity, and preserves input after failure', async () => {
		mocks.createNote.mockResolvedValueOnce({
			slug: 'hello',
			title: 'Hello',
			content: 'Body',
			type: 'note',
			status: 'draft',
			revision: 1,
			tags: [],
			hidden: false
		})
		render(<ContentEditor mode='create' type='note' />)
		fireEvent.change(screen.getByLabelText('标题'), { target: { value: 'Hello' } })
		fireEvent.change(screen.getByPlaceholderText('从这里开始写作...'), { target: { value: 'Body' } })
		fireEvent.click(screen.getByRole('button', { name: '保存草稿' }))
		await waitFor(() => expect(window.location.pathname).toBe('/manage/notes/hello'))
		expect(mocks.createNote).toHaveBeenCalledTimes(1)
		expect(screen.getByDisplayValue('Body')).toBeInTheDocument()
	})

	it('keeps the draft visible and reports a conflict instead of overwriting it', async () => {
		mocks.updateNote.mockRejectedValueOnce(Object.assign(new Error('server changed'), { status: 409 }))
		render(
			<ContentEditor
				mode='edit'
				type='note'
				initial={{ slug: 'hello', title: 'Old', content: 'Local draft', tags: [], hidden: false, status: 'draft', revision: 3 }}
			/>
		)
		fireEvent.click(screen.getByRole('button', { name: '保存草稿' }))
		await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('保存冲突'))
		expect(screen.getByDisplayValue('Local draft')).toBeInTheDocument()
	})

	it('confirms publish in a keyboard-contained dialog', () => {
		render(<ContentEditor mode='create' type='note' />)
		fireEvent.change(screen.getByLabelText('标题'), { target: { value: 'Hello' } })
		fireEvent.change(screen.getByPlaceholderText('从这里开始写作...'), { target: { value: 'Body' } })
		fireEvent.click(screen.getByRole('button', { name: '发布' }))
		expect(screen.getByRole('dialog')).toBeInTheDocument()
		fireEvent.keyDown(document, { key: 'Escape' })
		expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
	})

	it('serializes a queued publish with the latest draft and returned revision', async () => {
		let resolveDraft!: (value: unknown) => void
		const draftSave = new Promise(resolve => {
			resolveDraft = resolve
		})
		mocks.updateNote.mockReturnValueOnce(draftSave).mockResolvedValueOnce({
			slug: 'hello',
			title: 'New title',
			content: 'New body',
			type: 'note',
			status: 'published',
			revision: 5,
			tags: [],
			hidden: false
		})
		render(
			<ContentEditor
				mode='edit'
				type='note'
				initial={{ slug: 'hello', title: 'Old title', content: 'Old body', tags: [], hidden: false, status: 'draft', revision: 4 }}
			/>
		)

		fireEvent.change(screen.getByLabelText('标题'), { target: { value: 'New title' } })
		fireEvent.change(screen.getByPlaceholderText('从这里开始写作...'), { target: { value: 'New body' } })
		fireEvent.click(screen.getByRole('button', { name: '保存草稿' }))
		fireEvent.click(screen.getByRole('button', { name: '发布' }))
		fireEvent.click(screen.getByRole('button', { name: '确认发布' }))

		resolveDraft({ slug: 'hello', title: 'New title', content: 'New body', type: 'note', status: 'draft', revision: 5, tags: [], hidden: false })
		await waitFor(() => expect(mocks.updateNote).toHaveBeenCalledTimes(2))
		expect(mocks.updateNote.mock.calls[1][0]).toBe('hello')
		expect(mocks.updateNote.mock.calls[1][1]).toMatchObject({ expected_revision: 5, title: 'New title', content: 'New body', status: 'published' })
	})

	it('keeps published intent and latest input available for retry after failure', async () => {
		mocks.updateNote.mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce({
			slug: 'hello',
			title: 'Edited title',
			content: 'Edited body',
			type: 'note',
			status: 'published',
			revision: 4,
			tags: [],
			hidden: false
		})
		render(
			<ContentEditor
				mode='edit'
				type='note'
				initial={{ slug: 'hello', title: 'Old title', content: 'Old body', tags: [], hidden: false, status: 'draft', revision: 3 }}
			/>
		)
		fireEvent.change(screen.getByLabelText('标题'), { target: { value: 'Edited title' } })
		fireEvent.change(screen.getByPlaceholderText('从这里开始写作...'), { target: { value: 'Edited body' } })
		fireEvent.click(screen.getByRole('button', { name: '发布' }))
		fireEvent.click(screen.getByRole('button', { name: '确认发布' }))
		await waitFor(() => expect(screen.getByRole('button', { name: '保存失败，重试' })).toBeInTheDocument())

		fireEvent.change(screen.getByLabelText('标题'), { target: { value: 'Edited title again' } })
		fireEvent.click(screen.getByRole('button', { name: '保存失败，重试' }))
		await waitFor(() => expect(mocks.updateNote).toHaveBeenCalledTimes(2))
		expect(mocks.updateNote.mock.calls[1][1]).toMatchObject({ expected_revision: 3, title: 'Edited title again', content: 'Edited body', status: 'published' })
	})

	it('returns to editing when metadata changes', async () => {
		render(
			<ContentEditor
				mode='edit'
				type='blog'
				initial={{
					slug: 'hello',
					title: 'Title',
					content: 'Body',
					summary: 'Summary',
					category: 'Tech',
					tags: [],
					hidden: false,
					status: 'draft',
					revision: 1
				}}
			/>
		)
		fireEvent.click(screen.getByRole('button', { name: /属性/ }))
		fireEvent.change(screen.getByPlaceholderText('摘要'), { target: { value: 'New summary' } })
		expect(screen.getByText('编辑中')).toBeInTheDocument()
		fireEvent.click(screen.getByRole('checkbox'))
		await waitFor(() => expect(screen.getByText('编辑中')).toBeInTheDocument())
	})

	it('shows reduced-motion-safe saving feedback and aggregates attributes after save', async () => {
		let resolveSave!: (value: unknown) => void
		mocks.updateNote.mockReturnValueOnce(
			new Promise(resolve => {
				resolveSave = resolve
			})
		)
		render(
			<ContentEditor
				mode='edit'
				type='note'
				initial={{ slug: 'hello', title: 'Title', content: 'Body', tags: [], hidden: false, status: 'draft', revision: 1 }}
			/>
		)
		fireEvent.click(screen.getByRole('button', { name: /属性/ }))
		expect(screen.getByRole('region', { name: '内容属性' })).toBeInTheDocument()
		fireEvent.click(screen.getByRole('button', { name: '保存草稿' }))
		expect(screen.getByText('保存中...')).toHaveClass('animate-pulse', 'motion-reduce:animate-none')
		resolveSave({ slug: 'hello', title: 'Title', content: 'Body', type: 'note', status: 'draft', revision: 2, tags: [], hidden: false })
		await waitFor(() => expect(screen.queryByRole('region', { name: '内容属性' })).not.toBeInTheDocument())
	})

	it('aggregates attributes when focus moves to blank editor space', () => {
		render(
			<ContentEditor
				mode='edit'
				type='note'
				initial={{ slug: 'hello', title: 'Title', content: 'Body', tags: [], hidden: false, status: 'draft', revision: 1 }}
			/>
		)
		fireEvent.click(screen.getByRole('button', { name: /属性/ }))
		fireEvent.pointerDown(screen.getByTestId('editor-background'))
		expect(screen.queryByRole('region', { name: '内容属性' })).not.toBeInTheDocument()
	})

	it('inerts the editor background and restores focus after closing publish dialog', () => {
		render(<ContentEditor mode='create' type='note' />)
		const publish = screen.getByRole('button', { name: '发布' })
		fireEvent.change(screen.getByLabelText('标题'), { target: { value: 'Hello' } })
		fireEvent.change(screen.getByPlaceholderText('从这里开始写作...'), { target: { value: 'Body' } })
		publish.focus()
		fireEvent.click(publish)
		const background = screen.getByTestId('editor-background')
		expect(background).toHaveAttribute('aria-hidden', 'true')
		expect(background).toHaveAttribute('inert')
		fireEvent.click(screen.getByRole('button', { name: '取消' }))
		expect(publish).toHaveFocus()
	})
})
