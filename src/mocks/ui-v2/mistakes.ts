import type { ReviewTask } from '../../contracts/ui-v2/review-task'
import type { UiPageModel } from '../../contracts/ui-v2/ui-state'

const mockMistakes: ReviewTask[] = [
	{ id: 'mock-m1', title: 'Mock：解析几何错题', subject: '数学', priority: 'medium', status: 'pending', source: 'mock' },
]

export const mockMistakesNormal: UiPageModel<ReviewTask[]> = { state: 'ready', data: mockMistakes, error: null, source: 'mock' }
export const mockMistakesEmpty: UiPageModel<ReviewTask[]> = { state: 'empty', data: [], error: null, source: 'mock' }
export const mockMistakesLoading: UiPageModel<ReviewTask[]> = { state: 'loading', data: null, error: null, source: 'mock' }
export const mockMistakesError: UiPageModel<ReviewTask[]> = { state: 'error', data: null, error: 'mock: 错题加载失败', source: 'mock' }
export const mockMistakesPartial: UiPageModel<ReviewTask[]> = { state: 'partial', data: mockMistakes, error: null, source: 'mock' }
export const mockMistakesOverdue: UiPageModel<ReviewTask[]> = { state: 'ready', data: [], error: null, source: 'mock' }
