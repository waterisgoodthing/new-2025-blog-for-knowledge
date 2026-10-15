import type { ReviewTask } from '../../contracts/ui-v2/review-task'
import type { UiPageModel } from '../../contracts/ui-v2/ui-state'

const mockQueue: ReviewTask[] = [
	{ id: 'mock-r1', title: 'Mock：函数单调性错题', subject: '数学', priority: 'high', status: 'pending', source: 'mock' },
	{ id: 'mock-r2', title: 'Mock：牛顿第二定律', subject: '物理', priority: 'medium', status: 'pending', source: 'mock' },
]

export const mockReviewNormal: UiPageModel<ReviewTask[]> = { state: 'ready', data: mockQueue, error: null, source: 'mock' }
export const mockReviewEmpty: UiPageModel<ReviewTask[]> = { state: 'empty', data: [], error: null, source: 'mock' }
export const mockReviewLoading: UiPageModel<ReviewTask[]> = { state: 'loading', data: null, error: null, source: 'mock' }
export const mockReviewError: UiPageModel<ReviewTask[]> = { state: 'error', data: null, error: 'mock: 复习队列加载失败', source: 'mock' }
export const mockReviewPartial: UiPageModel<ReviewTask[]> = { state: 'partial', data: mockQueue.slice(0, 1), error: null, source: 'mock' }
export const mockReviewOverdue: UiPageModel<ReviewTask[]> = { state: 'ready', data: [], error: null, source: 'mock' }
