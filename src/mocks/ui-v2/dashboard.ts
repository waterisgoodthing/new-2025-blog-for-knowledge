import type { ReviewTask } from '../../contracts/ui-v2/review-task'
import type { UiPageModel } from '../../contracts/ui-v2/ui-state'

const mockTasks: ReviewTask[] = [
	{ id: 'mock-t1', title: 'Mock：今日复习 12 项', subject: '数学', priority: 'high', status: 'pending', source: 'mock' },
	{ id: 'mock-t2', title: 'Mock：错题再答 5 项', subject: '物理', dueAt: '2026-09-13', priority: 'medium', status: 'overdue', source: 'mock' },
]

export const mockDashboardNormal: UiPageModel<ReviewTask[]> = { state: 'ready', data: mockTasks, error: null, source: 'mock' }
export const mockDashboardEmpty: UiPageModel<ReviewTask[]> = { state: 'empty', data: [], error: null, source: 'mock' }
export const mockDashboardLoading: UiPageModel<ReviewTask[]> = { state: 'loading', data: null, error: null, source: 'mock' }
export const mockDashboardError: UiPageModel<ReviewTask[]> = { state: 'error', data: null, error: 'mock: 加载失败，请重试', source: 'mock' }
export const mockDashboardPartial: UiPageModel<ReviewTask[]> = { state: 'partial', data: mockTasks.slice(0, 1), error: null, source: 'mock' }
export const mockDashboardOverdue: UiPageModel<ReviewTask[]> = { state: 'ready', data: mockTasks.filter(t => t.status === 'overdue'), error: null, source: 'mock' }
