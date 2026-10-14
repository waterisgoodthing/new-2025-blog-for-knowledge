import type { UiPageModel } from '../../contracts/ui-v2/ui-state'
import type { Mistake } from '../../lib/api/mistakes'

// Canonical mistake mocks (U4). source: 'mock'; reviewItemId mirrors the shape
// of the real DTO (present vs absent) without inventing review semantics.

const mockDtos: Mistake[] = [
	{
		id: 'mock-mistake-1',
		source_draft_item_id: 'mock-draft-1',
		question_id: 'mock-q-1',
		subject_id: 1,
		title: 'Mock：函数单调性区间求错',
		question_text: '求 f(x)=x³-3x 的单调区间',
		my_answer: '增区间 (0,+∞)',
		correct_answer: '增区间 (-∞,-1),(1,+∞)',
		analysis: '导数符号判断遗漏负半轴',
		reason_category: 'concept',
		mistake_reason: '导数变号点找全了吗？',
		difficulty: 'medium',
		status: 'active',
		visibility: 'private',
		version: 1,
		knowledge_point_ids: [11, 12],
		review_item_id: 'mock-review-1',
		created_at: '2026-09-10',
		updated_at: '2026-09-14',
	},
	{
		id: 'mock-mistake-2',
		source_draft_item_id: 'mock-draft-2',
		question_id: 'mock-q-2',
		subject_id: 2,
		title: null,
		question_text: '牛顿第二定律应用：斜面加速度',
		my_answer: 'a = g',
		correct_answer: 'a = g·sinθ',
		analysis: null,
		reason_category: 'careless',
		mistake_reason: null,
		difficulty: null,
		status: 'archived',
		visibility: 'private',
		version: 2,
		knowledge_point_ids: [],
		review_item_id: '',
		created_at: '2026-09-01',
		updated_at: '2026-09-02',
	},
]

export function mockMistakeDtos(): Mistake[] {
	return mockDtos
}

export const mockMistakesV2Normal: UiPageModel<Mistake[]> = {
	state: 'ready',
	data: mockDtos,
	error: null,
	source: 'mock',
}

export const mockMistakesV2Empty: UiPageModel<Mistake[]> = {
	state: 'empty',
	data: [],
	error: null,
	source: 'mock',
}

export const mockMistakesV2Loading: UiPageModel<Mistake[]> = {
	state: 'loading',
	data: null,
	error: null,
	source: 'mock',
}

export const mockMistakesV2Error: UiPageModel<Mistake[]> = {
	state: 'error',
	data: null,
	error: 'mock: 错题加载失败，请重试',
	source: 'mock',
}

export const mockMistakesV2Partial: UiPageModel<Mistake[]> = {
	state: 'partial',
	data: mockDtos.slice(0, 1),
	error: 'mock: 部分错题暂不可用',
	source: 'mock',
}
