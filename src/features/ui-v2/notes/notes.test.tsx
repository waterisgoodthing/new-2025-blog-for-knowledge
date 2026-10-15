import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { adaptNoteArtifact } from '../../../adapters/ui-v2/from-backend'
import {
	mockNoteDtos,
	mockNotesV2Empty,
	mockNotesV2Error,
	mockNotesV2Loading,
	mockNotesV2Normal,
} from '../../../mocks/ui-v2/notes-v2'
import { Uiv2NotesSection } from './NotesSection'

describe('adaptNoteArtifact', () => {
	it('splits legacy free-text knowledge points without inventing IDs', () => {
		const [artifact] = mockNoteDtos().map(adaptNoteArtifact)
		expect(artifact).toMatchObject({
			id: 'mock-note-1',
			slug: 'mock-single-tone',
			subjectLabel: '数学',
			editorHref: '/manage/notes/mock-single-tone',
			source: 'backend',
		})
		expect(artifact.knowledgePoints).toEqual(['函数单调性', '导数'])
		expect(artifact.tags).toEqual(['数学'])
	})

	it('tolerates null tags and encodes slugs in the editor href', () => {
		const [dto] = mockNoteDtos()
		const artifact = adaptNoteArtifact({
			...dto,
			slug: 'a b/c',
			tags: null as unknown as [],
			knowledge_points: undefined,
		})
		expect(artifact.tags).toEqual([])
		expect(artifact.knowledgePoints).toEqual([])
		expect(artifact.editorHref).toBe('/manage/notes/a%20b%2Fc')
	})
})

describe('Uiv2NotesSection', () => {
	it('renders artifacts with relations and an editor entry link', () => {
		const models = mockNotesV2Normal.data?.map(adaptNoteArtifact) ?? []
		render(
			<Uiv2NotesSection model={{ state: 'ready', data: models, error: null, source: 'mock' }} />,
		)
		expect(screen.getByText('Mock：单调性学习笔记')).toBeInTheDocument()
		expect(screen.getByText('函数单调性')).toBeInTheDocument()
		expect(screen.getByRole('link', { name: '在编辑器中打开' })).toHaveAttribute(
			'href',
			'/manage/notes/mock-single-tone',
		)
	})

	it('covers loading / empty / error states', () => {
		const { rerender } = render(<Uiv2NotesSection model={mockNotesV2Loading} />)
		expect(screen.getByRole('status', { name: '正在加载笔记' })).toBeInTheDocument()

		rerender(<Uiv2NotesSection model={mockNotesV2Empty} />)
		expect(screen.getByText('还没有笔记，学完一个知识点后记一笔吧。')).toBeInTheDocument()

		rerender(<Uiv2NotesSection model={mockNotesV2Error} />)
		expect(screen.getByRole('alert')).toHaveTextContent('mock: 笔记加载失败，请重试')
	})
})
