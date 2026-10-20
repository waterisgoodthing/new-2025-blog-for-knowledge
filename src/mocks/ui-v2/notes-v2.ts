import type { UiPageModel } from '../../contracts/ui-v2/ui-state'
import type { NoteDetail } from '../../lib/api/notes'

// Note artifact mocks (U8). Raw DTO shapes; adaptation asserted in tests.

const mockDto: NoteDetail = {
	id: 'mock-note-1',
	slug: 'mock-single-tone',
	title: 'Mock：单调性学习笔记',
	type: 'note',
	status: 'published',
	hidden: false,
	created_at: '2026-09-10',
	updated_at: '2026-09-14',
	tags: [{ id: 1, name: '数学' }],
	sort_order: 0,
	revision: 3,
	summary: '导数符号决定单调性，注意变号点',
	subject: '数学',
	knowledge_points: '函数单调性、导数',
	content: '# 单调性\n\n...',
}

export function mockNoteDtos(): NoteDetail[] {
	return [mockDto]
}

export const mockNotesV2Normal: UiPageModel<NoteDetail[]> = {
	state: 'ready',
	data: [mockDto],
	error: null,
	source: 'mock',
}

export const mockNotesV2Empty: UiPageModel<NoteDetail[]> = {
	state: 'empty',
	data: [],
	error: null,
	source: 'mock',
}

export const mockNotesV2Loading: UiPageModel<NoteDetail[]> = {
	state: 'loading',
	data: null,
	error: null,
	source: 'mock',
}

export const mockNotesV2Error: UiPageModel<NoteDetail[]> = {
	state: 'error',
	data: null,
	error: 'mock: 笔记加载失败，请重试',
	source: 'mock',
}
