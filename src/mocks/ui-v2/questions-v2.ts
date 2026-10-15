import type { UiPageModel } from '../../contracts/ui-v2/ui-state'
import type { Question as QuestionDto } from '../../lib/api/questions'

// Canonical question mocks (U6): raw DTO shapes adapted by adaptQuestion.
// source provenance is asserted post-adaptation in tests.

const mockDto: QuestionDto = {
	id: 'mock-question-1',
	subject_id: 1,
	title: 'Mock：单调性选择题',
	stem_md: '求 f(x)=x³-3x 的单调递增区间',
	question_text: '求 f(x)=x³-3x 的单调递增区间',
	question_type: 'single_choice',
	options: [
		{ key: 'A', text: '(0,+∞)' },
		{ key: 'B', text: '(-∞,-1),(1,+∞)' },
		{ key: 'C', text: '(-1,1)' },
	],
	answer_data: { kind: 'single_choice', value: 'B' },
	correct_answer: 'B',
	analysis_md: '求导 f′(x)=3x²-3，令 f′>0 得 x<-1 或 x>1',
	explanation: null,
	difficulty: 'medium',
	status: 'active',
	visibility: 'private',
	version: 1,
	knowledge_point_ids: [11],
	sources: [],
	created_at: '2026-09-10',
	updated_at: '2026-09-14',
}

export function mockQuestionDtos(): QuestionDto[] {
	return [mockDto, bareDto]
}

const bareDto: QuestionDto = {
	id: 'mock-question-2',
	subject_id: 2,
	title: null,
	stem_md: '',
	question_text: '简述牛顿第二定律',
	question_type: 'short_answer',
	options: [],
	answer_data: { kind: 'short_answer', value: '' },
	correct_answer: null,
	analysis_md: null,
	explanation: null,
	difficulty: 'unspecified',
	status: 'active',
	visibility: 'private',
	version: 1,
	knowledge_point_ids: [],
	sources: [],
	created_at: '2026-09-01',
	updated_at: '2026-09-02',
}

export const mockQuestionsV2Normal: UiPageModel<QuestionDto[]> = {
	state: 'ready',
	data: [mockDto, bareDto],
	error: null,
	source: 'mock',
}

export const mockQuestionsV2Empty: UiPageModel<QuestionDto[]> = {
	state: 'empty',
	data: [],
	error: null,
	source: 'mock',
}

export const mockQuestionsV2Loading: UiPageModel<QuestionDto[]> = {
	state: 'loading',
	data: null,
	error: null,
	source: 'mock',
}

export const mockQuestionsV2Error: UiPageModel<QuestionDto[]> = {
	state: 'error',
	data: null,
	error: 'mock: 题库加载失败，请重试',
	source: 'mock',
}
